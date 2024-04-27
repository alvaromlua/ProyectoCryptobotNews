from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from fastai.text.all import *
import pandas as pd
from sklearn import preprocessing

# Define la variable global learn_cls
global_learn_cls = None

def load_model():
    
    df = pd.read_excel('Datos_noticias_fin_tot.xlsx')
    print("\n---------------------------- Instanciamos nuestro codificador de labels ----------------------------\n")
    encoder = preprocessing.LabelEncoder()

    print("\n---------------------------- Alimentamos con la información de las categorias ----------------------------\n")
    
    encoder.fit(df["overall_sentiment"])

    df_class = pd.DataFrame(data = {
        "text": df["Noticia_preprocesado"],
        "ref": encoder.transform(df["overall_sentiment"])
        })
    
    print("\n---------------------------- Dividimos el conjunto de datos en 2: entrenamiento (90%) y pruebas (10%) ----------------------------\n")
    
    df_train, df_test = train_test_split(df_class, test_size=0.1, random_state=2023)
    
    print("\n---------------------------- Cargar el tokenizador y el modelo preentrenado ----------------------------\n")
    
    model_name = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    print("\n---------------------------- Preparación del conjunto de datos de lenguaje ----------------------------\n")
    
    data_lm = TextDataLoaders.from_df(df_train, valid_pct=0.2, text_col="text", label_col="ref", is_lm=True, tokenizer=tokenizer)
    
    print("\n---------------------------- Entrenamiento del modelo de lenguaje ----------------------------\n")
    
    learn_lm = language_model_learner(data_lm, AWD_LSTM, drop_mult=0.7, metrics=accuracy)
    suggested_lr = learn_lm.lr_find()
    learn_lm.fit_one_cycle(1, lr_max=suggested_lr.valley)
    learn_lm.unfreeze()
    learn_lm.fit_one_cycle(5, lr_max=slice(suggested_lr.valley/(2.6**4), suggested_lr.valley))
    learn_lm.save_encoder("ft_lm_distilroberta")

    data_cls = TextDataLoaders.from_df(df_train, valid_pct=0.2, text_col="text", label_col="ref", is_lm=False, tokenizer=tokenizer)
    learn_cls = text_classifier_learner(data_cls, AWD_LSTM, drop_mult=0.7, metrics=accuracy)
    learn_cls = learn_cls.load_encoder("ft_lm_distilroberta")
    suggested_lr = learn_cls.lr_find()
    learn_cls.fit_one_cycle(1, lr_max=suggested_lr.valley)
    learn_cls.unfreeze()
    learn_cls.fit_one_cycle(5, lr_max=slice(suggested_lr.valley/(2.6**4), suggested_lr.valley))

    print("\n---------------------------- Guardamos el modelo en la variable global ----------------------------\n")

    global_learn_cls = learn_cls


def get_resultado_noticias(texto_ejemplo):
    
    if global_learn_cls is None:
        raise ValueError("El modelo no ha sido cargado. Por favor, ejecuta primero load_model().")
    
    clase_a_etiqueta = {0: "Negative", 1: "Positive"}
    prediccion = global_learn_cls.predict(texto_ejemplo)
    clase_predicha = clase_a_etiqueta[int(prediccion[0])]
    
    return clase_predicha


if __name__ == '__main__':
    load_model()
