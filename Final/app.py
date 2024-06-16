from flask import Flask, request, render_template, redirect, url_for
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
import os

# 以下資訊可以從 Azure 電腦視覺服務取得(正式上線時不要直接把金鑰跟服務端點寫在程式碼裡)
C_KEY = '791027e760634f8d89d71eeefa60a550'  # 填入金鑰
C_ENDPOINT = 'https://rg10173239.cognitiveservices.azure.com/'  # 填入端點

# 以下資訊可以從 Azure 翻譯服務取得(正式上線時不要直接把金鑰跟服務端點寫在程式碼裡)
T_REGION = 'eastus'  # 填入位置/區域
T_KEY = '0b7696ffcd2042d68b7f8cdf0a4f9289'  # 填入金鑰
T_ENDPOINT = 'https://api.cognitive.microsofttranslator.com/'  # 填入文字翻譯的 Web API

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def ImageAnalysis(image_path, local=False):
    client = ComputerVisionClient(
        endpoint=C_ENDPOINT,
        credentials=CognitiveServicesCredentials(C_KEY)
    )
    if local:
        with open(image_path, "rb") as image_stream:
            analysis = client.describe_image_in_stream(image_stream, max_candidates=1, language="en")
    else:
        analysis = client.describe_image(url=image_path, max_candidates=1, language="en")

    return analysis.captions[0]

def Translator(target, lang):
    text_translator = TextTranslationClient(
        endpoint=T_ENDPOINT,
        credential=TranslatorCredential(T_KEY, T_REGION)
    )
    targets = [InputTextItem(text=target)]
    
    responses = text_translator.translate(content=targets, to=[lang], from_parameter="en")
    
    return responses

@app.route("/", methods=['GET', 'POST'])
def object_detection():
    translation_result = None
    if request.method == 'POST':
        lang = request.form.get('lang')
        
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return "No selected file"
            if file:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(image_path)
                text_en = ImageAnalysis(image_path, local=True)
        else:
            image_url = request.form.get('image_url')
            text_en = ImageAnalysis(image_url)
        
        text_translated = Translator(text_en.text, lang)
        translation_result = text_translated[0].translations[0].text

    return render_template('index.html', translation_result=translation_result)

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    return redirect(url_for('object_detection'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
