from flask import Flask, request, render_template
import io, base64
import matplotlib.pyplot as plt
import numpy as np

from portfolio.data import compute_benchmark
from portfolio.optim import portfolios
from portfolio.plotting import graph


def create_app():
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        error = None
        results = None

        if request.method == "POST":
            tickers = [t.strip().upper() for t in request.form.get("tickers", "").split(",") if t.strip()]
            benchmark = request.form.get("benchmark", "").strip()

            wr_raw = request.form.get("wanted_return", "").strip()
            wv_raw = request.form.get("wanted_volatility", "").strip()
            rf_raw = request.form.get("rf", "").strip()

            # interpret inputs
            wanted_return = (float(wr_raw) / 100 if wr_raw else "blank")
            wanted_volatility = (float(wv_raw) / 100 if wv_raw else None)
            rf = float(rf_raw) / 100 if rf_raw else 0.0

            bm_point = None
            bm_sp = None
            if benchmark:
                mean_r, sigma, sharpe = compute_benchmark(benchmark, rf)
                bm_point = (mean_r, sigma)
                bm_sp = sharpe

            view = (request.form.get("view") or "mvp").strip().lower()
            show_tickers = bool(request.form.get("show_tickers"))

            try:
                all_results = portfolios(tickers, wanted_return, wanted_volatility, rf)

                # render graph
                fig = graph(
                    tickers, wanted_return, wanted_volatility, rf,
                    view=view, benchmark=bm_point, show_tickers=show_tickers,
                    benchmark_label=benchmark or None
                )
                plt.figure(fig.number)
                x_min, x_max = plt.xlim()
                y_min, y_max = plt.ylim()
                left, bottom, width, height = plt.gca().get_position().bounds
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=140, transparent=True)
                plt.close(fig)
                img_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

                def portfolio_table(names, weights_vec):
                    weights = np.asarray(weights_vec).reshape(-1)
                    return [(n, float(w)) for n, w in zip(names, weights)]

                results = {}
                results["tickers"] = tickers
                results["rf"] = rf
                results["target_mu"] = (
                    float(wanted_return)
                    if (isinstance(wanted_return, (int, float)) or (isinstance(wanted_return, str) and wanted_return.strip().lower() != "blank"))
                    else float(all_results[14])
                )
                results["target_sigma"] = (
                    "-" if (isinstance(wanted_return, str) and wanted_return.strip().lower() != "blank")
                    else (f"{wanted_volatility:.4f}" if wanted_volatility is not None else "-")
                )
                results["view"] = view

                # unpack "everything" (kept same indices as your original)
                results["mvp_weights"] = portfolio_table(tickers, all_results[0])
                results["mvp_r"] = float(all_results[1])
                results["mvp_s"] = float(all_results[2])

                results["tangent_weights"] = portfolio_table(tickers, all_results[7])
                results["tangent_r"] = float(all_results[8])
                results["tangent_s"] = float(all_results[9])

                results["opt_norf_weights"] = portfolio_table(tickers, all_results[3])
                results["opt_norf_r"] = float(all_results[14])
                results["opt_norf_s"] = float(all_results[4])

                results["opt_rf_weights"] = portfolio_table(tickers, all_results[10]) + [("CASH", all_results[11])]
                results["opt_rf_r"] = float(all_results[15])
                results["opt_rf_s"] = float(all_results[12])

                results["plot_b64"] = img_b64

                results["mvp_sp"] = float(all_results[16])
                results["op_sp"] = float(all_results[17])
                results["tp_sp"] = float(all_results[18])

                results["bm_sp"] = float(bm_sp) if benchmark else None

                results["x_min"] = float(x_min); results["x_max"] = float(x_max)
                results["y_min"] = float(y_min); results["y_max"] = float(y_max)
                results["ax_left"] = float(left); results["ax_bottom"] = float(bottom)
                results["ax_width"] = float(width); results["ax_height"] = float(height)

            except Exception as e:
                error = str(e)

        return render_template("index.html", results=results, error=error)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
