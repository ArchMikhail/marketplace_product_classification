import json
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC


def clean_data(src):
    """Function that perform cleaning of data"""

    # �������� html �����
    flag = True
    while flag:
        pos1 = src.find('<')
        if pos1 == -1:
            flag = False
        pos2 = src.find('>')
        if pos2 == -1:
            flag = False
        if pos1 != -1:
            if pos2 != -1:
                if pos1 < pos2:
                    src = src[0 : pos1] + ' ' + src[pos2 + 1:]
                else:
                    flag = False

    # �������� ����������������� �������� html
    src = src.replace('&nbsp;',' ')
    src = src.replace('&lt;',' ')
    src = src.replace('&gt;',' ')
    src.strip()

    # �������� ��������� ������� ��������
    flag = True
    while flag:
        pos1 = src.find('  ')
        if pos1 == -1:
            flag = False
        else:
            src = src.replace('  ',' ')

    return src


# ������ ��������
print('Train data reading...')
df = pd.read_parquet('train.parquet', engine='pyarrow')
df.reset_index(drop=True, inplace=True)
dataset = df['text_fields']
shop_list = df['shop_title']

# ���������� ������������ ����� � ������������ ������ ��� �����������
print('Train data preparation...')
data_for_tokenization = [json.loads(dataset[i])['title'] + ' ' +
                        json.loads(dataset[i])['title'] + ' ' +
                        json.loads(dataset[i])['title'] + ' ' +
                        json.loads(dataset[i])['title'] + ' ' +
                        shop_list[i] + ' ' + shop_list[i] + ' ' +
                        json.loads(dataset[i])['description'] + ' ' +
                        str(json.loads(dataset[i])['attributes']) + ' ' +
                        str(json.loads(dataset[i])['custom_characteristics']) + ' ' +
                        str(json.loads(dataset[i])['defined_characteristics'])
                        for i in range(len(dataset))]

# ������ ������
cleaned_data = [clean_data(data_for_tokenization[i]) for i in range(len(data_for_tokenization))]

# ����������� ������
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(cleaned_data)

# ������������� �����
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

# ������ ������ ������� ����������
Y = [df['category_id'][i] for i in range(len(df['category_id']))]

# �������� ������
print('Model training...')
model = OneVsRestClassifier(LinearSVC(random_state=0, C=1.8), n_jobs=12).fit(X_train_tfidf, Y)
print('Model trained')


# ������ ��������� ��������
print('Test data reading...')
df_test = pd.read_parquet('test.parquet', engine='pyarrow')
df_test.reset_index(drop=True, inplace=True)
dataset_test = df_test['text_fields']
shop_list_test = df_test['shop_title']

# ���������� ������������ ����� � ������������ ������ ��� �����������
print('Test data preparation...')
data_for_tokenization_test = [json.loads(dataset_test[i])['title'] + ' ' +
                             json.loads(dataset_test[i])['title'] + ' ' +
                             json.loads(dataset_test[i])['title'] + ' ' +
                             json.loads(dataset_test[i])['title'] + ' ' +
                             shop_list_test[i] + ' ' + shop_list_test[i] + ' ' +
                             json.loads(dataset_test[i])['description'] + ' ' +
                             str(json.loads(dataset_test[i])['attributes']) + ' ' +
                             str(json.loads(dataset_test[i])['custom_characteristics']) + ' ' +
                             str(json.loads(dataset_test[i])['defined_characteristics'])
                             for i in range(len(dataset_test))]

# ������ ������
cleaned_data_test = [clean_data(data_for_tokenization_test[i]) for i in range(len(data_for_tokenization_test))]

# ����������� ������
X_test_counts = count_vect.transform(cleaned_data_test)

# ������������� �����
X_test_tfidf = tfidf_transformer.transform(X_test_counts)

# ������������
print('Data prediction...')
predicted = model.predict(X_test_tfidf)
print('Prediction done')


# ��������� ���������
df_out = pd.DataFrame(list(zip(df_test['product_id'], predicted)),
                     columns=['product_id', 'predicted_category_id'])
df_out.to_parquet('result.parquet', engine = 'pyarrow', index=False)
print('Data saved')