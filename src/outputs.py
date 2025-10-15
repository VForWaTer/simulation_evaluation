from pathlib import Path
import json
import subprocess
import shutil
from json2args.logger import logger
import re
from jinja2 import FileSystemLoader, Environment
from plotly.utils import PlotlyJSONEncoder

def create_output_resources(data_names, catchment_plots, catchment_metrics):
    logger.info("#Tcreate output ressources - simulation evaluation")
    report_root = Path("report")
    static_plots = report_root / "static" / "plots"     
    lib_dir      = report_root / "src" / "lib"
    static_plots.mkdir(parents=True, exist_ok=True)
    lib_dir.mkdir(parents=True, exist_ok=True)

    def safe(name: str) -> str:
        return re.sub(r'[^A-Za-z0-9._-]+', '_', name)

    # 1) Write each plot as a JSON file under report/static/plots
    index = {}
    for name, plot in catchment_plots.items():
        fn = f"{safe(name)}.json"
        (static_plots / fn).write_text(
            json.dumps(plot, cls=PlotlyJSONEncoder, separators=(',', ':')),
            encoding="utf-8"
        )
        # This URL will be valid in both dev & prod builds
        index[name] = f"/plots/{fn}"

    # 2) move metrics to static if large; otherwise keep as JS
    # Here we keep metrics small in JS:
    (lib_dir / "report_data.js").write_text(
        "export const names = " + json.dumps(data_names, ensure_ascii=False, separators=(',', ':')) + ";\n"
        "export const metrics = " + json.dumps(catchment_metrics, ensure_ascii=False, separators=(',', ':')) + ";\n",
        encoding="utf-8"
    )

    # 3) A tiny index mapping catchment -> json URL
    (lib_dir / "plot_index.js").write_text(
        "export const plotIndex = " + json.dumps(index, ensure_ascii=False, separators=(',', ':')) + ";\n",
        encoding="utf-8"
    )

    # 4) Library barrel
    (lib_dir / "config.js").write_text(
        'export const config = { title: "Simulation Evaluation Report" };\n',
        encoding="utf-8"
    )
    (lib_dir / "index.ts").write_text(
        "export { names, metrics } from './report_data.js';\n"
        "export { plotIndex } from './plot_index.js';\n"
        "export { config } from './config.js';\n",
        encoding="utf-8"
    )
    logger.info("#Tcreate output ressources - End")

def create_output_resources_old(data_names, catchment_plots, catchment_metrics):
    logger.info("#Tcreate output ressources - simulation evaluation")

    try:
    
        report_src = Path('.') / "report" / "src"
        report_lib = report_src / "lib"
        logger.info("Done 1")

        
        # Create lib directory if it doesn't exist
        report_lib.mkdir(parents=True, exist_ok=True)

        plots_path = report_lib / "plot_data.js"
        with open(plots_path, "w", encoding="utf-8") as f:
            f.write("export const plots = {")
            first = True
            for name, plot in catchment_plots.items():
                if not first:
                    f.write(",")
                first = False
                # key
                json.dump(name, f, ensure_ascii=False)
                f.write(":")
                # value (compact JSON for size/speed)
                json.dump(plot, f, ensure_ascii=False, separators=(',', ':'))
                # optional: flush periodically for huge outputs
                # f.flush()
            f.write("};")


        # Create plot_data.js
        #with open(report_lib / "plot_data.js", "w") as f:
        #    logger.info("befor")
        #    f.write(f"export const plots = {json.dumps(catchment_plots, indent=4)}")
        #    logger.info("fter")
        logger.info("Done 2")

        (report_lib / "report_data.js").write_text(
        "export const metrics = " +
        json.dumps(catchment_metrics, ensure_ascii=False, separators=(',', ':')) +
        ";\n\nexport const names = " +
        json.dumps(data_names, ensure_ascii=False, separators=(',', ':')) +
        ";\n",
        encoding="utf-8"
        )

        (report_lib / "config.js").write_text(
            'export const config = {\n  title: "Simulation Evaluation Report"\n};\n',
            encoding="utf-8"
        )
        (report_lib / "index.ts").write_text(
            "export { plots } from './plot_data.js';\n"
            "export { metrics, names } from './report_data.js';\n"
            "export { config } from './config.js';\n",
            encoding="utf-8"
        )
        logger.info("Done 5")
    except Exception as e:
        logger.info(str(e))


def build_report():
    logger.info("build Report- simulation evaluation")
    try:
        report_src = Path('.') / "report"
        print(report_src)

        subprocess.run(["npm", "install"], cwd=report_src)
        subprocess.run(["npm", "run", "build"], cwd=report_src)

        shutil.copy(report_src / "build" / "index.html", "/out/simulation_report.html")
    except Exception as e:
        logger.info(str(e))



def create_output(data_names, catchment_plots, catchment_tables, catchment_metrics):
    logger.info("create output - simulation evaluation")
    try:
        templateLoader = FileSystemLoader('./templates')
        env = Environment(loader=templateLoader)
        
        json_plots = json.dumps(catchment_plots)
        json_tables = json.dumps(catchment_tables)
        json_metrics = json.dumps(catchment_metrics)
        
        template = env.get_template('default.html')
        html_content = template.render(data_names=data_names, json_plots=json_plots, json_tables=json_tables, json_metrics=json_metrics)
        
        with open("/out/output.html", "w") as f:
            f.write(html_content)
    except Exception as e:
        logger.info(str(e))
