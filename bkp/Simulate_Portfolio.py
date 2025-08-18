# %% [markdown]
# ### Abaixo está uma implementação em Python de simulate_portfolio(n_contracts=10_000, seed=42) que cria um DataFrame de contratos com distribuições distintas por produto, converte probabilidade anual de default em mensal e projeta as parcelas mensais (incluindo simulação de inadimplência e recuperação). A função retorna dois DataFrames: df_portfolio e df_cashflows.

# %%
# Importando bibliotecas que serão utilizadas para a geração dos dados
import numpy as np
import pandas as pd
import os

# %% [markdown]
# ## Gera uma carteira sintética de contratos e seus fluxos de caixa projetados.
# ### df_portfolio: DataFrame com colunas  
# ####        - contract_id  
# ####        - product_type  (financiamento, consignado, cartão)  
# ####        - principal     (valor atual)  
# ####        - interest_rate (ao mês, em decimal, ex: 0.02 = 2% a.m.)  
# ####        - term_months   (prazo restante)  
# ####        - default_prob  (probabilidade anual de default, em decimal)  
# ####        - default_prob_m (probabilidade mensal derivada)  
# ####       - recovery_rate (percentual recuperável em default, em decimal)  
# ####        - default_month (mês do default, 1..term, ou NaN se sem default)  
#   
# ###      df_cashflows: DataFrame com colunas  
# ####        - contract_id  
# ####        - month  
# ####        - product_type  
# ####        - scheduled_payment        (parcela calculada pela Tabela Price)  
# ####        - interest_component       (juros do mês)  
# ####        - principal_component      (amortização do mês)  
# ####        - remaining_principal_before  
# ####        - remaining_principal_after  
# ####        - defaulted_this_month     (bool)  
# ####        - recovery_cashflow        (entrada de recuperação no mês do default)

# %%
def simulate_portfolio(n_contracts=10_000, seed=42):
    rng = np.random.default_rng(seed)  
  
    # 1) Distribuições por produto  
    product_types = np.array(["financiamento", "consignado", "cartao"])  
    # Pesos (exemplo): 45% financiamento, 35% consignado, 20% cartão  
    product_weights = np.array([0.45, 0.35, 0.20])  
    products = rng.choice(product_types, size=n_contracts, p=product_weights, replace=True)  
  
    # Aloca arrays  
    principal = np.empty(n_contracts, dtype=float)  
    interest_rate_m = np.empty(n_contracts, dtype=float)  
    term_months = np.empty(n_contracts, dtype=int)  
    default_prob_a = np.empty(n_contracts, dtype=float)  
    recovery_rate = np.empty(n_contracts, dtype=float)  
  
    # Helpers para amostragem por produto  
    idx_fin = products == "financiamento"  
    idx_con = products == "consignado"  
    idx_car = products == "cartao"  
  
    # Financiamento: valores maiores, taxa média, prazo médio/longo, prob anual média, recuperação média  
    n_fin = idx_fin.sum()  
    if n_fin > 0:  
        principal[idx_fin] = rng.lognormal(mean=np.log(60000), sigma=0.5, size=n_fin).clip(30000, 150000)  
        interest_rate_m[idx_fin] = rng.normal(loc=0.018, scale=0.004, size=n_fin).clip(0.006, 0.03)  
        term_months[idx_fin] = rng.integers(24, 85, size=n_fin)  # 24-84  
        default_prob_a[idx_fin] = rng.normal(loc=0.06, scale=0.02, size=n_fin).clip(0.02, 0.12)  
        recovery_rate[idx_fin] = rng.normal(loc=0.55, scale=0.10, size=n_fin).clip(0.30, 0.80)  
  
    # Consignado: valores médios, taxa mais baixa, prazo médio, prob anual baixa, recuperação alta  
    n_con = idx_con.sum()  
    if n_con > 0:  
        principal[idx_con] = rng.lognormal(mean=np.log(18000), sigma=0.5, size=n_con).clip(5000, 60000)  
        interest_rate_m[idx_con] = rng.normal(loc=0.013, scale=0.003, size=n_con).clip(0.006, 0.025)  
        term_months[idx_con] = rng.integers(12, 73, size=n_con)  # 12-72  
        default_prob_a[idx_con] = rng.normal(loc=0.025, scale=0.01, size=n_con).clip(0.005, 0.05)  
        recovery_rate[idx_con] = rng.normal(loc=0.65, scale=0.10, size=n_con).clip(0.40, 0.90)  
  
    # Cartão: valores menores, taxa alta, "prazo" curto para projeção, prob anual alta, recuperação baixa  
    n_car = idx_car.sum()  
    if n_car > 0:  
        principal[idx_car] = rng.lognormal(mean=np.log(2500), sigma=0.7, size=n_car).clip(400, 15000)  
        interest_rate_m[idx_car] = rng.normal(loc=0.075, scale=0.02, size=n_car).clip(0.03, 0.15)  
        term_months[idx_car] = rng.integers(6, 37, size=n_car)  # 6-36 (proxy para projeção)  
        default_prob_a[idx_car] = rng.normal(loc=0.14, scale=0.05, size=n_car).clip(0.06, 0.30)  
        recovery_rate[idx_car] = rng.normal(loc=0.25, scale=0.08, size=n_car).clip(0.05, 0.45)  
  
    # 2) Converter probabilidade anual -> mensal  
    # p_m = 1 - (1 - p_a) ** (1/12)  
    default_prob_m = 1.0 - np.power(1.0 - default_prob_a, 1.0 / 12.0)  
  
    # 3) Simular default (mês do default via distribuição geométrica)  
    # Geometric(k) ~ número de tentativas até o sucesso; default no mês k.  
    # Se k > prazo, consideramos "sem default".  
    geom_draws = np.ceil(rng.geometric(p=default_prob_m, size=n_contracts)).astype(int)  
    default_month = geom_draws.astype(float)  # começamos como float para permitir NaN  
    # Onde a chance mensal é "muito baixa", a geométrica pode explodir — trataremos naturalmente com prazo  
    no_default_mask = geom_draws > term_months  
    default_month[no_default_mask] = np.nan  
  
    # Monta df_portfolio  
    df_portfolio = pd.DataFrame({  
        "contract_id": np.arange(1, n_contracts + 1, dtype=int),  
        "product_type": products,  
        "principal": principal,  
        "interest_rate": interest_rate_m,  
        "term_months": term_months,  
        "default_prob": default_prob_a,  
        "default_prob_m": default_prob_m,  
        "recovery_rate": recovery_rate,  
        "default_month": default_month  
    })  
  
    # 4) Gerar fluxo de caixa (Tabela Price com interrupção no default e recuperação no mês do default)  
    # Observação: para cartão, isso é uma aproximação (parcelado com pagamento fixo).  
    cashflow_rows = []  
    for i in range(n_contracts):  
        cid = i + 1  
        P = principal[i]  
        r = interest_rate_m[i]  
        n = term_months[i]  
        d_m = default_month[i]  # float ou NaN  
        rec = recovery_rate[i]  
        prod = products[i]  
  
        # Parcela mensal (Price)  
        if r <= 0:  
            payment = P / n  
        else:  
            payment = P * r / (1.0 - (1.0 + r) ** (-n))  
  
        remaining = P  
        default_triggered = False  
        d_m_int = int(d_m) if not np.isnan(d_m) else None  
  
        for m in range(1, n + 1):  
            if default_triggered:  
                # Após o default, não há novos fluxos (encerramos a projeção deste contrato)  
                break  
  
            rem_before = remaining  
            # Checa se o default acontece neste mês ANTES do pagamento (assumimos que sim)  
            defaulted_this_month = (d_m_int is not None) and (m == d_m_int)  
  
            if defaulted_this_month:  
                # Sem pagamento regular; aplica recuperação sobre o saldo devedor corrente  
                interest_component = 0.0  
                principal_component = 0.0  
                rem_after = rem_before  # saldo não muda pela parcela (não houve)  
                recovery = rec * rem_before  
                default_triggered = True  
                # Após a recuperação, assumimos encerramento (sem parcelas futuras)  
                # Não alteramos rem_after por recuperação (é um fluxo separado)  
                cashflow_rows.append({  
                    "contract_id": cid,  
                    "month": m,  
                    "product_type": prod,  
                    "scheduled_payment": 0.0,  
                    "interest_component": interest_component,  
                    "principal_component": principal_component,  
                    "remaining_principal_before": rem_before,  
                    "remaining_principal_after": rem_after,  
                    "defaulted_this_month": True,  
                    "recovery_cashflow": recovery  
                })  
                # Encerra o loop deste contrato  
                break  
            else:  
                # Pagamento normal  
                interest_component = rem_before * r  
                principal_component = payment - interest_component  
                # Evita cair negativo por arredondamentos no último mês  
                if principal_component > rem_before:  
                    principal_component = rem_before  
                    payment_effective = interest_component + principal_component  
                else:  
                    payment_effective = payment  
                rem_after = rem_before - principal_component  
  
                cashflow_rows.append({  
                    "contract_id": cid,  
                    "month": m,  
                    "product_type": prod,  
                    "scheduled_payment": float(payment_effective),  
                    "interest_component": float(interest_component),  
                    "principal_component": float(principal_component),  
                    "remaining_principal_before": float(rem_before),  
                    "remaining_principal_after": float(rem_after),  
                    "defaulted_this_month": False,  
                    "recovery_cashflow": 0.0  
                })  
  
                remaining = rem_after  
  
                # Se o saldo zerou, encerra antes do prazo  
                if remaining <= 1e-8:  
                    break  
  
        # Caso não tenha havido default e o saldo não tenha sido completamente quitado por alguma razão numérica,  
        # não fazemos nada adicional (Price normalmente zera).  
  
    df_cashflows = pd.DataFrame(cashflow_rows)  
  
    return df_portfolio, df_cashflows

# %%
df_portfolio, df_cashflows = simulate_portfolio(n_contracts=10000, seed=42)

# %%
print(df_portfolio.head())
print(df_portfolio.tail())

# %%
print(df_cashflows.head())
print(df_cashflows.tail())

# %%
# Garante que as pastas existam
os.makedirs("data", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# %%
# Exportação dos CSVs para reuso
df_portfolio.to_csv("data/portifolio.csv", index=False)
df_cashflows.to_csv("data/cashflows.csv", index=False)


