from flask import Flask, send_from_directory, jsonify
import os
import requests

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory(app.root_path, "index.html")

@app.route("/api/ativo/<papel>")
def ativo(papel):
    try:
        papel = papel.upper()

        # Cotação + indicadores fundamentalistas
        r = requests.get(
            f"https://brapi.dev/api/quote/{papel}",
            params={"fundamental": "true", "dividends": "true"},
            timeout=20
        )
        data = r.json()

        if "error" in data or not data.get("results"):
            return jsonify({"error": f"Papel '{papel}' não encontrado"}), 404

        q = data["results"][0]
        fi = q.get("fundamentalIndicators") or {}
        dv = (q.get("dividendsData") or {})
        dy = dv.get("yield") if dv else None

        result = {
            "papel":            papel,
            "tipo":             "ON" if papel.endswith("3") else "PN" if papel.endswith("4") else "",
            "empresa":          q.get("longName") or q.get("shortName", ""),
            "setor":            q.get("sector", ""),
            "subsetor":         q.get("industry", ""),
            "cotacao":          q.get("regularMarketPrice"),
            "data_ult_cot":     q.get("regularMarketTime", ""),
            "min_52_sem":       q.get("fiftyTwoWeekLow"),
            "max_52_sem":       q.get("fiftyTwoWeekHigh"),
            "vol_med_2m":       q.get("averageDailyVolume3Month"),
            "valor_de_mercado": q.get("marketCap"),
            "valor_da_firma":   q.get("enterpriseValue"),
            "nro_acoes":        q.get("sharesOutstanding"),
            "indicadores": {
                "pl":            q.get("priceEarnings") or fi.get("priceEarnings"),
                "pvp":           fi.get("priceToBook"),
                "pebit":         fi.get("priceToEbit"),
                "psr":           fi.get("psr"),
                "p_ativos":      fi.get("priceToAssets"),
                "div_yield":     dy,
                "ev_ebitda":     fi.get("enterpriseValue_Ebitda"),
                "ev_ebit":       fi.get("enterpriseValue_Ebit"),
                "lpa":           q.get("epsTrailingTwelveMonths"),
                "vpa":           fi.get("bookValuePerShare"),
                "marg_bruta":    q.get("grossMargins"),
                "marg_ebit":     q.get("ebitdaMargins"),
                "marg_liquida":  q.get("profitMargins"),
                "ebit_ativo":    fi.get("ebitByAssets"),
                "roic":          fi.get("returnOnInvestedCapital"),
                "roe":           q.get("returnOnEquity"),
                "liquidez_corr": fi.get("currentRatio"),
                "div_br_patrim": fi.get("debtToEquity"),
                "giro_ativos":   fi.get("assetTurnover"),
                "cres_rec_5a":   fi.get("revenueGrowth5y"),
            },
            "balanco": {
                "ativo":            fi.get("totalAssets"),
                "disponibilidades": fi.get("cash"),
                "ativo_circulante": fi.get("currentAssets"),
                "div_bruta":        fi.get("totalDebt"),
                "div_liquida":      fi.get("netDebt"),
                "patrim_liq":       fi.get("netPatrimony"),
            },
            "resultados": {
                "ultimos_12m": {
                    "receita_liquida": fi.get("netRevenue12m"),
                    "ebit":            fi.get("ebit12m"),
                    "lucro_liquido":   fi.get("netIncome12m"),
                },
                "ultimos_3m": {
                    "receita_liquida": fi.get("netRevenue3m"),
                    "ebit":            fi.get("ebit3m"),
                    "lucro_liquido":   fi.get("netIncome3m"),
                },
            },
            "oscilacoes": {
                "dia":             q.get("regularMarketChangePercent"),
                "mes":             q.get("regularMarketChangePercent"),
                "trinta_dias":     None,
                "doze_meses":      q.get("fiftyTwoWeekHighChange"),
                "ano_corrente":    None,
                "ano_anterior":    None,
                "dois_anos_atras": None,
            },
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
