import plotly.express as px
import pandas as pd
import sys

input_filename = sys.argv[1]
output_html_filename = sys.argv[2]

df = pd.read_csv(input_filename, sep="\t", dtype=str)

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


# superclass_results
all_category = list(df["superclass_results"])
split_category = []
for category in all_category:
    if len(category) > 0:
        for split in category.split(","):
            split_category.append(split)

category_counts_df = pd.DataFrame()
category_counts_df["superclass"] = split_category
category_counts_df = category_counts_df.groupby("superclass").size().reset_index(name="count")

fig_superclass = px.pie(pathway_counts_df, values='count', names='superclass', title='SuperClass Pie Chart')

# class_results
all_category = list(df["class_results"])
split_category = []
for category in all_category:
    if len(category) > 0:
        for split in category.split(","):
            split_category.append(split)

category_counts_df = pd.DataFrame()
category_counts_df["class"] = split_category
category_counts_df = category_counts_df.groupby("class").size().reset_index(name="count")

fig_class = px.pie(pathway_counts_df, values='count', names='class', title='Class Pie Chart')


with open(output_html_filename, 'a') as f:
    f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write(fig_superclass.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write(fig_class.to_html(full_html=False, include_plotlyjs='cdn'))