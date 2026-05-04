import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from difflib import get_close_matches
from uuid import uuid4
import json
import os

llm = ChatOllama(model="mistral", temperature=0.1)


# step 1 - load csv
def load_csv(path):
    if not os.path.exists(path):
        raise FileNotFoundError("CSV not found")

    df = pd.read_csv(path)

    if df.empty:
        raise ValueError("CSV is empty")

    # normalize column names
    df.columns = [c.lower().strip() for c in df.columns]

    # convert numeric like columns
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    # fill Missing values
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].mean())

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Unknown")

    return df


# step 2 : LLM decide operation


def decide_operation(question, columns):
    prompt = f"""
You are a data analyst.

Available columns: {list(columns)}

Return ONLY JSON:
{{
  "operation": "mean|max|min|sum|count",
  "column": "column name",
  "groupby": "column name or null"
}}

Rules:
- Use ONLY given column names exactly as shown
- Do NOT invent column names
- groupby must be a categorical column or null
"""

    response = llm.invoke(
        [SystemMessage(content=prompt), HumanMessage(content=question)]
    )

    raw = response.content.strip().replace("```json", "").replace("```", "")

    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except:
        return None


def validate(config, df):
    if not config:
        return None

    column = config.get("column")
    groupby = config.get("groupby")
    operation = config.get("operation")

    if column not in df.columns:
        return None

    if groupby and groupby not in df.columns:
        groupby = None
        config["groupby"] = None

    if operation not in ["mean", "max", "min", "sum", "count"]:
        return None

    if operation != "count":
        if not pd.api.types.is_numeric_dtype(df[column]):
            return None

    return config


def execute(df, config):
    col = config["column"]
    grp = config["groupby"]
    op = config["operation"]

    if grp:
        grouped = df.groupby(grp)[col]
        if op == "mean":
            return grouped.mean().round(2)
        if op == "sum":
            return grouped.sum().round(2)
        if op == "count":
            return grouped.count()
        if op == "max":
            return grouped.max()
        if op == "min":
            return grouped.min()
    else:
        if op == "mean":
            return round(df[col].mean(), 2)
        if op == "sum":
            return round(df[col].sum(), 2)
        if op == "count":
            return df[col].count()
        if op == "max":
            return df[col].max()
        if op == "min":
            return df[col].min()


def detect_chart(question):
    keywords = ["show", "plot", "chart", "graph", "distribution", "visualize"]
    return any(word in question.lower() for word in keywords)


def build_chart_config(config):
    col = config["column"]
    grp = config["groupby"]

    time_keywords = ["date", "month", "year", "week", "day", "time", "period"]

    if grp:
        grp_lower = grp.lower()

        if any(grp_lower.endswith(word) for word in time_keywords):
            chart_type = "line"
        else:
            chart_type = "bar"

    else:
        chart_type = "histogram"

    return {
        "type": chart_type,
        "column": col,
        "groupby": grp,
        "operation": config["operation"],
    }


def plot_chart(df, config, chart_config, output_dir):
    try:
        plt.figure(figsize=(8, 5))
        sns.set_theme(style="whitegrid")

        filename = f"chart_{uuid4().hex[:6]}.png"
        path = os.path.join(output_dir, filename)

        # ── HISTOGRAM ─────────────────────────────
        if chart_config["type"] == "histogram":
            sns.histplot(df[chart_config["column"]], bins=10, kde=False)
            plt.xlabel(chart_config["column"].replace("_", " ").title())
            plt.ylabel("Count")
            plt.title(
                f"Distribution of {chart_config['column'].replace('_', ' ').title()}"
            )

        # ── BAR CHART ─────────────────────────────
        elif chart_config["type"] == "bar":
            result = execute(df, config)

            if config["groupby"]:
                data = result.reset_index()
                data.columns = [config["groupby"], config["column"]]

                sns.barplot(data=data, x=config["groupby"], y=config["column"])

                plt.xticks(rotation=45)

            else:
                sns.barplot(x=[config["column"]], y=[result])

            plt.xlabel(
                config["groupby"].replace("_", " ").title()
                if config["groupby"]
                else config["column"].title()
            )
            plt.ylabel(f"{config['operation'].title()} of {config['column'].title()}")
            plt.title(
                f"{config['operation'].title()} of {config['column'].title()}"
                + (f" by {config['groupby'].title()}" if config["groupby"] else "")
            )

        # ── LINE CHART ─────────────────────────────
        elif chart_config["type"] == "line" and config["groupby"]:
            result = execute(df, config)
            data = result.reset_index()

            x_col = config["groupby"]

            # safer sorting (important)
            try:
                data[x_col] = pd.to_datetime(data[x_col])
            except:
                pass

            data = data.sort_values(x_col)

            # rename for clarity
            data.columns = [x_col, config["column"]]

            sns.lineplot(data=data, x=x_col, y=config["column"], marker="o")

            plt.xticks(rotation=45)
            plt.xlabel(x_col.replace("_", " ").title())
            plt.ylabel(f"{config['operation'].title()} of {config['column'].title()}")
            plt.title(
                f"{config['operation'].title()} of {config['column'].title()} over {x_col.replace('_', ' ').title()}"
            )

        else:
            return None

        plt.tight_layout()
        plt.savefig(path)
        plt.close()

        return path

    except Exception as e:
        print(f"Chart error: {e}")
        plt.close()
        return None


def generate_insight(question, result, config):
    if hasattr(result, "to_dict"):
        summary = result.to_dict()
    else:
        summary = result

    response = llm.invoke(
        [
            SystemMessage(
                content=f"""You are a data analyst.
Give a 2-3 sentence insight using specific numbers.
Operation: {config["operation"]} of {config["column"]}
Result: {summary}"""
            ),
            HumanMessage(content=question),
        ]
    )

    return response.content


def ask_csv(question, df, output_dir="."):
    if not question or len(question.strip()) < 3:
        return "Please ask a valid question.", None

    if df is None or df.empty:
        return "No data available.", None

    config = decide_operation(question, df.columns)
    config = validate(config, df)

    if not config:
        return "Could not understand question. Please use exact column names.", None

    result = execute(df, config)

    if detect_chart(question):
        chart_config = build_chart_config(config)
        chart_path = plot_chart(df, config, chart_config, output_dir)
        insight = generate_insight(question, result, config)
        return insight, chart_path

    insight = generate_insight(question, result, config)
    return insight, None
