import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.kernel_ridge import KernelRidge
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
from joblib import load
import plotly.graph_objects as go
import plotly.io as pio
import time
from explainerdashboard import ClassifierExplainer, ExplainerDashboard
from explainerdashboard.dashboard_components import ImportancesComponent, ShapContributionsTableComponent, ShapContributionsGraphComponent
from sklearn.preprocessing import LabelEncoder
import streamlit.components.v1 

st.set_option('deprecation.showPyplotGlobalUse', False)

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("./Maternal Health Risk Data Set.csv")
    target = 'RiskLevel'
    return df, target

# Train Logistic Regression model
@st.cache_resource
def load_model():
    model = load("./random_forest_model.pkl")
    return model

# Display results
def display_results(model, X_train, y_train, X_test, y_test):
    y_pred_test = model.predict(X_test)
    y_pred_train = model.predict(X_train)
    
    accuracy_test = accuracy_score(y_test, y_pred_test)
    accuracy_train = accuracy_score(y_train, y_pred_train)
    cm = confusion_matrix(y_test, y_pred_test)
    
    accuracy_df = pd.DataFrame({
        "Split": ["Train", "Test"],
        "Accuracy": [f"{accuracy_train*100:.2f}%", f"{accuracy_test*100:.2f}%"],
        "# samples": [f"{len(y_train)}", f"{len(y_test)}"]
    })
    st.write("**Accuracy:**")
    accuracy_df = accuracy_df.style.set_properties(**{'text-align': 'left'})
    accuracy_df.set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
    st.dataframe(accuracy_df, width=500, hide_index=True)

    fig = go.Figure(data=go.Heatmap(
                    z=cm[::-1],
                    x=['High Risk', 'Low Risk', 'Medium Risk'],  
                    y=['Medium Risk', 'Low Risk', 'High Risk'],  
                    hoverongaps=False,
                    text=cm[::-1],
                    colorscale="blues",
                    texttemplate="%{text}"))
    
    fig.update_layout(
        title='Confusion Matrix',
        xaxis_title="Predicted",
        yaxis_title="True")

    st.plotly_chart(fig)
    plt.clf()  # Clear the current figure after displaying it
    
def main():
    st.header("About the Model", anchor="model")
    st.title("Maternal Health Risk Prediction")
    st.logo(
        "./love.png",
        icon_image="./heartbeat.gif",
    )
    st.write("\n\n")
    st.subheader("Model Training and Evaluation", anchor="training", divider="red")
    
    st.write("**Model**: [Random Forest](https://willkoehrsen.github.io/data%20science/machine%20learning/random-forest-simple-explanation/)")
    
    with st.popover("🚀 **Hyperparameters**"):
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.write("- [criterion](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#:~:text=100%20in%200.22.-,criterion,-%7B%E2%80%9Cgini%E2%80%9D%2C%20%E2%80%9Centropy%E2%80%9D%2C%20%E2%80%9Clog_loss): log_loss")
        with c2:
            st.write("- [max_depth](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#:~:text=is%20tree%2Dspecific.-,max_depth,-int%2C%20default%3DNone): 15")
        with c3:
            st.write("- [max_features](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#:~:text=is%20not%20provided.-,max_features,-%7B%E2%80%9Csqrt%E2%80%9D%2C%20%E2%80%9Clog2%E2%80%9D%2C%20None): log2")
        with c4:
            st.write("- [n_estimators](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#:~:text=Parameters%3A-,n_estimators,-int%2C%20default%3D100): 100")
        st.write("The above mentioned hyperparameters are the result of hyperparameter tuning using [GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html#gridsearchcv) using a 4 fold cross-validation.")

    df, target = load_data()
    X = df.drop(target, axis=1)
    y = df[target]
    if 'X_train' not in st.session_state:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7)
        st.session_state.X_train = X_train
        st.session_state.y_train = y_train
        st.session_state.X_test = X_test
        st.session_state.y_test = y_test
    else:
        X_train = st.session_state.X_train
        y_train = st.session_state.y_train
        X_test = st.session_state.X_test
        y_test = st.session_state.y_test
    st.write(f"Training on **{len(X_train)}** samples and using **{len(X_test)}** samples for validation.")
    model = load_model()
    with st.spinner(text='Training...'):
        start_time = time.time()
        model.fit(X_train, y_train)
        training_time = time.time() - start_time
    st.write(f"**Training time**: {training_time:.2f} seconds")    
    st.toast('Training Complete !!', icon="✔️")
        
    st.write("\n\n\n")
    st.subheader("Model Performance", anchor="model-performance", divider="red")
    display_results(model, X_train, y_train, X_test, y_test)
    # st.write("One can see that the accuracy is quite good.")
    st.write("By looking at the confusion matrix, we can see that our model does a good job in reducing the number of false positives i.e. if the actual is *:red[High Risk]*, only a few instances are predicted as *:green[Low Risk]* or *:orange[Medium Risk]*.")
    st.write("This is important because in the context of maternal health, we want to minimize the number of false positives as much as possible i.e. a *:red[High Risk]* and *:orange[Medium Risk]* should not be predicted as *:green[Low Risk]* as much as possible.")
    st.write("The inverse is okay i.e. if a *:green[Low Risk]* is predicted as *:orange[Medium Risk]* or *:red[High Risk]*, it is not as bad as the former case.")    
    with st.expander("💡 Click here to know more about the confusion matrix..."):
        st.write("The accuracy metric only gives the overall corectness of the model.")
        st.write("In order to get a better understanding of the model's performance across different classes, the confusion matrix is more valueable.")
        st.write("The confusion matrix shows the actual v.s. predicted classification for each class.")
        
    st.write("\n\n")
    help_str = "We do not use the model co-efficeints as feature importances because the value of each co-efficient depends on the scale of the input features. For example, if we use months as a unit for Age instead of years, the coefficient for Age will be 12 times smaller which does not make sense.\nThis means that the magnitude of a coefficient is not necessarily a good measure of a feature’s importance.\nHence, SHAP values are used to calculate feature importances."
    st.subheader("Feature Importances", anchor="feature-importances", help=help_str, divider="red")
    st.write("Using [:blue-background[ExplainerDashboard]](https://github.com/oegedijk/explainerdashboard) for our model, we visualize feature importances.")
    
    y_train = LabelEncoder().fit_transform(y_train)
    y_test = LabelEncoder().fit_transform(y_test)
    model = model.fit(X_train, y_train)
    
    with st.container():
        st.write("\n\n")
        with st.spinner(text='Loading Explainer...'):
            if 'explainer' not in st.session_state:
                explainer = ClassifierExplainer(model, X_test, y_test)
                st.session_state.explainer = explainer
                explainer.dump("./explainer.joblib")
            else:
                explainer = ClassifierExplainer.from_file("./explainer.joblib")
            
            importances_component = ImportancesComponent(explainer, hide_title=True)
            importances_html = importances_component.to_html()
            st.components.v1.html(importances_html, height=440, width=800, scrolling=False)
       
    # st.toast('Explainer loaded', icon="✔️")
    st.write("From the plot above, we can see that the most prominent feature for the model in its decision making is *BS* i.e blood sugar levels")
    st.write("This gives an overview of the model's decision making process. However, if we want to see the contributions for a single sample, click on 'Individual Predictions' in the sidebar.") 
    
    with st.expander("📚 **General Note**"):
        st.write('We do not use the model co-efficeints as feature importances because the value of each co-efficient depends on the scale of the input features. For example, if we use months as a unit for Age instead of years, the coefficient for Age will be 12 times smaller which does not make sense.')
        st.write("This means that the magnitude of a coefficient is not necessarily a good measure of a feature’s importance.")
        st.write("Hence, SHAP values are used to calculate feature importances.")
    with st.expander("🤯 **What are SHAP values**? 🎲"):
        st.write("Shapley values are a concept from game theory that provide a natural way to compute which features contribute to a prediction or contribute to the uncertainty of a prediction.")
        st.write("A prediction can be explained by assuming that each feature value of the instance is a 'player' in a game where the prediction is the payout.")
        st.info("The SHAP value of a feature is **not** the difference of the predicted value after removing the feature from the model training. It can be interpreted as - given the current set of feature values, the contribution of a feature value to the difference between the actual prediction and the mean prediction is the estimated Shapley value.", icon="ℹ️")
    
    
if __name__ == "__main__":
    main()
