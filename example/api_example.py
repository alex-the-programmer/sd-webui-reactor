import base64, io, requests, json
from PIL import Image, PngImagePlugin
from datetime import datetime, date

address = 'http://127.0.0.1:7860'
input_file = "extensions\sd-webui-roop-nsfw\example\IamSFW.jpg" # Input file path
time = datetime.now()
today = date.today()
current_date = today.strftime('%Y-%m-%d')
current_time = time.strftime('%H-%M-%S')
output_file = 'outputs/api/output_'+current_date+'_'+current_time+'.png' # Output file path
try:
    im = Image.open(input_file)
except Exception as e:
    print(e)
finally:
    print(im)

img_bytes = io.BytesIO()
im.save(img_bytes, format='PNG') 
img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

# Roop-GE arguments:
args=[
    img_base64, #0
    True, #1 Enable Roop-GE
    '0', #2 Comma separated face number(s) from swap-source image
    '0', #3 Comma separated face number(s) for target image (result)
    'C:\stable-diffusion-webui\models/roop\inswapper_128.onnx', #4 model path
    'CodeFormer', #4 Restore Face: None; CodeFormer; GFPGAN
    1, #5 Restore visibility value
    True, #7 Restore face -> Upscale
    '4x_NMKD-Superscale-SP_178000_G', #8 Upscaler (type 'None' if doesn't need), see full list here: http://127.0.0.1:7860/sdapi/v1/script-info -> roop-ge -> sec.8
    2, #9 Upscaler scale value
    1, #10 Upscaler visibility (if scale = 1)
    False, #11 Swap in source image
    True, #12 Swap in generated image
]

# The args for roop-ge can be found by 
# requests.get(url=f'{address}/sdapi/v1/script-info')

prompt = "(8k, best quality, masterpiece, highly detailed:1.1),realistic photo of fantastic happy woman,hairstyle of blonde and red short bob hair,modern clothing,cinematic lightning,film grain,dynamic pose,bokeh,dof"

neg = "ng_deepnegative_v1_75t,(badhandv4:1.2),(worst quality:2),(low quality:2),(normal quality:2),lowres,(bad anatomy),(bad hands),((monochrome)),((grayscale)),(verybadimagenegative_v1.3:0.8),negative_hand-neg,badhandv4,nude,naked,(strabismus),cross-eye,heterochromia,((blurred))"

payload = {
    "prompt": prompt,
    "negative_prompt": neg,
    "seed": -1,
    "sampler_name": "DPM++ 2M Karras",
    "steps": 15,
    "cfg_scale": 7,
    "width": 512,
    "height": 768,
    "restore_faces": False,
    "alwayson_scripts": {"roop-ge":{"args":args}}
}

try:
    print('Working... Please wait...')
    result = requests.post(url=f'{address}/sdapi/v1/txt2img', json=payload)
except Exception as e:
    print(e)
finally:
    print('Done! Saving file...')

if result is not None:
    r = result.json()

    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{address}/sdapi/v1/png-info', json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        try:
            image.save(output_file, pnginfo=pnginfo)
        except Exception as e:
            print(e)
        finally:
            print(f'{output_file} is saved\nAll is done!')
else:
    print('Something went wrong...')
