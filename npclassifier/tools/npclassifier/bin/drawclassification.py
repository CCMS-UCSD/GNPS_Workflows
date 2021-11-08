import plotly.express as px
import pandas as pd
import sys

input_filename = sys.argv[1]
output_html_filename = sys.argv[2]

df = pd.read_csv(input_filename, sep="\t")

print(df)

all_pathways = list(df["pathway_results"])
split_pathways = []
for pathway in all_pathways:
    if len(pathway) > 0:
        for split in pathway.split(","):
            split_pathways.append(split)

pathway_counts_df = pd.DataFrame()
pathway_counts_df["pathway"] = split_pathways
pathway_counts_df = pathway_counts_df.groupby("pathway").size().reset_index(name="count")

fig = px.pie(pathway_counts_df, values='count', names='pathway', title='Pathway Pie Chart')

with open(output_html_filename, 'a') as f:
    f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))