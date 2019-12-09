from collections import Counter

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from sklearn.metrics import cohen_kappa_score

SEPARATOR = ","


def binarize(label_list, label):
    binarized_labels = [label in item.split(SEPARATOR) for item in label_list]
    return binarized_labels


def evaluate_kappa(kappa):
    """ Return an evaluation of a particular Kappa value, using Fleiss's guidelines
    (see Wikipedia page)
    """
    if kappa < 0.4:
        return "Poor"
    elif kappa < 0.75:
        return "Fair"
    return "Excellent"


st.sidebar.title("Quill Annotation Tools")
st.sidebar.markdown(
    """
    Compute inter-annotator agreement
"""
)

st.title("Inter-annotator agreement")

labels1 = st.text_area("Paste the labels of the first annotator", value='label1\nlabel2,label3\nlabel2')
labels2 = st.text_area("Paste the labels of the second annotator", value='label1\nlabel2,label3\nlabel2')

if len(labels1) > 0 and len(labels2) > 0:
    label_list1 = labels1.split("\n")
    label_list2 = labels2.split("\n")

    flat_label_list1 = [l for item in label_list1 for l in item.split(SEPARATOR)]
    flat_label_list2 = [l for item in label_list2 for l in item.split(SEPARATOR)]

    unique_labels = list(set(flat_label_list1 + flat_label_list2))
    unique_labels.sort()

    st.header("Labels")

    st.text(f"Found {len(unique_labels)} labels:")
    st.write(unique_labels)

    st.header("Label frequencies")

    label_counter1 = Counter(flat_label_list1)
    label_counter2 = Counter(flat_label_list2)

    label_freqs1 = [label_counter1.get(l, 0) for l in unique_labels]
    label_freqs2 = [label_counter2.get(l, 0) for l in unique_labels]

    # df = pd.DataFrame({"annotator1": label_freqs1, "annotator2": label_freqs2}, index=unique_labels)
    # st.write(df)

    fig = go.Figure(data=[
        go.Bar(name='Annotator1', x=unique_labels, y=label_freqs1),
        go.Bar(name='Annotator2', x=unique_labels, y=label_freqs2)
    ])
    # Change the bar mode
    fig.update_layout(barmode='group')

    st.plotly_chart(fig)

    st.header("Inter-annotator agreement")

    if len(label_list1) != len(label_list2):
        st.text(f"Annotator1: {len(label_list1)} items")
        st.text(f"Annotator2: {len(label_list2)} items")
        st.text("Two annotators have different number of items. Cannot compute agreement.")

    else:
        kappas = []
        kappa_labels = []
        for label in unique_labels:
            binarized_labels1 = binarize(label_list1, label)
            binarized_labels2 = binarize(label_list2, label)

            kappa = cohen_kappa_score(binarized_labels1, binarized_labels2)
            kappas.append(kappa)
            kappa_labels.append(evaluate_kappa(kappa))

        df = pd.DataFrame({"kappa": kappas, "agreement": kappa_labels}, index=unique_labels)
        st.write(df)
