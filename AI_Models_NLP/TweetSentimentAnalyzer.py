import os
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import matplotlib.pyplot as plt
import re
import nltk
import pandas as pd
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from wordcloud import WordCloud


class TweetSentimentAnalyzer:
    def __init__(self):
        self.languages_dict = {'en': 'English', 'fr': 'French', 'es': 'Spanish', 'de': 'Deutsch'}

    def open_file(self, year, language, OG, analyzed):
        # Get the parent directory of the current working directory
        parent_dir = os.path.dirname(os.getcwd())
        data_dir = os.path.join(parent_dir, "Data")  # Construct the path to the 'Data' directory
        filename = f"tweets_data_{language}_{year}"
        if analyzed:
            filename += "_sentiment"
        else:
            if OG:
                filename += "_VO"
            elif OG == False:
                filename += "_VE"
            
        file_path = os.path.join(data_dir, filename + '.csv')
        try:
            return pd.read_csv(file_path, sep=',')
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
       

    # def get_file_name(self, year, language, OG):
    #     # Get the parent directory of the current working directory
    #     parent_dir = os.path.dirname(os.getcwd())
    #     data_dir = os.path.join(parent_dir, "Data")  # Construct the path to the 'Data' directory
    #     filename = f"tweets_data_{language}_{year}"
    #     if OG:
    #         filename += "_VO"
    #     else:
    #         filename += "_VE"
    #     file_path = os.path.join(data_dir, filename)
    #     return file_path

    def sentiment_analyzing(self, year, language):

        # Liste des noms de modèles à utiliser
        model_names = ["cardiffnlp/twitter-xlm-roberta-base-sentiment",
                    "yannLanglo/sentiment-analysis-Climate",
                    "EynardM/sentiment-analysis-Climate"]

        # Pour compter le nombre de fichiers CSV générés
        num_csv_files = 0

        # Boucle sur chaque modèle
        for model_name in model_names:
            print(f"Analyzing sentiment for {year} in {language} using model {model_name}...")
            # Charger le tokenizer et le modèle pour le modèle actuel
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)

            # Appliquer l'analyse de sentiment à chaque tweet avec le modèle actuel
            def analyze_sentiment(tweet):
                inputs = tokenizer(tweet, return_tensors="pt", truncation=True, padding=True, max_length=512)
                with torch.no_grad():
                    outputs = model(**inputs)
                scores = outputs[0][0].detach().numpy()
                scores = softmax(scores)
                positive_score = scores[2]  # Utiliser l'indice pour le score positif selon le modèle multilingue
                return 1 if positive_score > 0.5 else 0

            # Charger les données appropriées en fonction de la langue
            if language == 'en':
                tweets_data = self.open_file(year, language, None, False)
            else:
                tweets_data = pd.concat([self.open_file(year, language, True, False),
                                        self.open_file(year, language, False, False)], ignore_index=True)

            # Appliquer l'analyse de sentiment avec le modèle actuel
            tweets_data['sentiment'] = tweets_data['content'].apply(analyze_sentiment)

            # Sauvegarder les résultats dans un fichier CSV
            file_name = f'tweets_data_{year}_{language}_sentiment_{model_name.replace("/", "-")}.csv'
            self.save_to_csv(tweets_data, file_name)
            num_csv_files += 1

        # Retourner le nombre de fichiers CSV générés
        return num_csv_files


    def save_to_csv(self, dataframe, file_path):
        if os.path.exists(file_path):
            dataframe.to_csv(file_path, mode='a', index=False, header=False, encoding='utf-8')
        else:
            dataframe.to_csv(file_path, mode='w', index=False, encoding='utf-8')


    def wordcloud(self,years, language):
        nltk.download('stopwords')
        
        def clean_word(word):
            """Nettoyer les mots en retirant la ponctuation."""
            return re.sub(r'[^\w\s]', '', word).lower()

        # Mapping from short code to full language name for stopwords
        lang_dict = {
            'fr': 'french',
            'es': 'spanish',
            'en': 'english',
            'de': 'german'
        }
        
        # Mots vides personnalisés
        stop_words_personal = '''food waste climate change climat climatechange https http com www twitter pic status co amp www youtube foodwaste
        climatique changement climatique alimentaire déchets alimentaires comida residuos cambio climático alimentación'''
        stop_words_personal_set = set(stop_words_personal.split())

        # Calculer le nombre de lignes et de colonnes nécessaires pour les sous-graphiques
        num_years = len(years)
        num_cols = min(num_years, 3)  # Limiter à 3 colonnes au maximum
        num_rows = (num_years + num_cols - 1) // num_cols

        fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 5*num_rows))
    
        if num_years == 1:
            axes = [axes]

        for i, year in enumerate(years):
            if language == 'en':
                tweets_data = self.open_file(year, language, None, False)
            else:
                tweets_data = pd.concat([self.open_file(year, language, True, False),self.open_file(year, language, False, False)])
            
            stop_words_language = set(stopwords.words(lang_dict[language]))
            stop_words_en = set(stopwords.words('english'))

            # Fusionner tous les ensembles de mots vides pour obtenir un ensemble unique
            stop_words = stop_words_personal_set.union(stop_words_language).union(stop_words_en)

            # Ajouter une colonne 'year' au DataFrame
            tweets_data['year'] = tweets_data['published_at'].apply(lambda x: x.split('-')[0])

            # Dictionnaire pour stocker la fréquence des mots pour chaque année
            word_freq_year = {}

            # Boucle sur chaque tweet pour calculer la fréquence des mots par année
            for index, row in tweets_data.iterrows():
                tweet = row['content']
                tweet_year = row['year']
                words = tweet.split()
                for word in words:
                    word = clean_word(word)
                    if word not in stop_words and word != '':
                        if tweet_year not in word_freq_year:
                            word_freq_year[tweet_year] = {}
                        word_freq_year[tweet_year][word] = word_freq_year[tweet_year].get(word, 0) + 1

            # Créer des nuages de mots pour chaque année
            wordcloud_ax = axes[i]
            for year, word_freq in word_freq_year.items():
                wordcloud = WordCloud(width=400, height=200, background_color='white').generate_from_frequencies(word_freq)
                wordcloud_ax.imshow(wordcloud, interpolation='bilinear')
                wordcloud_ax.set_title(f"Word Cloud for Year {year} and language {language} on {len(tweets_data)} tweets")
                wordcloud_ax.axis('off')

        # Cacher les sous-graphiques inutilisés
        for i in range(num_years, num_rows * num_cols):
            axes[i].axis('off')

        plt.tight_layout()
        plt.show()



    def CircularGraph(self, years, language):
        num_years = len(years)
        cols = 2
        rows = (num_years + 1) // cols  # Calculate number of rows needed

        fig, axes = plt.subplots(rows, cols, figsize=(8, 4 * rows))
        axes = axes.flatten()  # Flatten in case we have more than 1 row

        for i, year in enumerate(years):
            try:
                tweets_data_analyzed = self.open_file(year, language, None, True)
            except:
                self.sentiment_analyzing(year, language)
                tweets_data_analyzed = self.open_file(year, language, None, True)

            positive_count = tweets_data_analyzed['sentiment'].sum()
            negative_count = len(tweets_data_analyzed) - positive_count

            labels = ['Positive', 'Negative']
            sizes = [positive_count, negative_count]
            colors = ['#DEB7BC', '#75343C']
            explode = (0.1, 0)  # explode 1st slice

            # Plot in the appropriate subplot
            axes[i].pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
            axes[i].set_title(f'Ratio of Positive and Negative Tweets\nfor {year} in {self.languages_dict[language]} on {len(tweets_data_analyzed)} Tweets')

        # Hide any unused subplots
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        plt.show()

    def CircularGraphPath(self,path):
        # Charger les données à partir du fichier CSV
        tweets_data_analyzed = pd.read_csv(path)

        # Compter le nombre de tweets positifs et négatifs
        positive_count = tweets_data_analyzed['sentiment'].sum()
        negative_count = len(tweets_data_analyzed) - positive_count

        # Créer les étiquettes et les tailles pour le diagramme circulaire
        labels = ['Positive', 'Negative']
        sizes = [positive_count, negative_count]
        colors = ['#DEB7BC', '#75343C']
        explode = (0.1, 0)  # explode 1st slice

        # Créer le diagramme circulaire
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.title('Ratio of Positive and Negative Tweets')

        # Afficher le diagramme circulaire
        plt.axis('equal')  # Assure que le cercle est dessiné comme un cercle
        plt.show()
        
if __name__ == "__main__":
    analyzer = TweetSentimentAnalyzer()
    
