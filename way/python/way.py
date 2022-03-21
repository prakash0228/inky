import json, requests, base64, epd7in5b, textwrap
from flask import Flask, request, Response, jsonify
from functools import wraps
from PIL import Image, ImageDraw, ImageFont

# Authenticate request
def check_auth(username, password):
  # ToDo validate URI
  url = "https://tjusandbox.service-now.com/api/x_thjuh_way/auth"
  data = json.dumps({'mac': getMAC('wlan0')})
  r = requests.post(url, data, auth=('wayAuth', '123456'))
  body = json.loads(r.text)
  return username == body['result']['Key']  and password == body['result']['Secret']

def authenticate():
  message = {'status': 401, 'message': "Authentication error",}
  resp = jsonify(message)
  resp.status_code = 401
  return resp

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.authorization
    if not auth:
      return authenticate()

    elif not check_auth(auth.username, auth.password):
      return authenticate()

    return f(*args, **kwargs)

  return decorated

# Return the MAC address of the specified interface
def getMAC(interface='wlan0'):
  try:
    str = open('/sys/class/net/%s/address' %interface).read()
  except:
    str = "00:00:00:00:00:00"

  return str[0:17]

# Initialize flask app
app = Flask(__name__)


# Test WAY App POST Request
@app.route("/way", methods=["POST"])
#@requires_auth
def way_status_update():
  wlan = getMAC('wlan0')
  try:
    print("RequestBody: "  + request.data.decode())
    body = json.loads(request.data.decode())
    if all (k in body for k in ("mac","msg", "name")):
      mac = str(body["mac"]).strip()
      Status = str(body["msg"]).strip()
      Name = str(body["name"]).strip()
      if(mac and Name and mac == wlan):
        msg = str({'mac': mac, 'msg': Status, 'name': Name})
        display(Name, Status)
        return Response(str({'status': 202, 'message': 'Status Updated. Request body: ' + msg}), status = 202, mimetype = 'application/json')
      else:
        return err_body("Invalid mac or msg or name in request body")
    else:
      return err_body("Invalid request body")

  except Exception as e:
    print("Exception: " + str(e))
    return err_body("")


# Invalid request body handler
@app.errorhandler(400)
def err_body(msg):
  if not str(msg).strip():
   msg = "Invalid request body"
  ex = str({"mac": "aa:11:bb:22:cc:33", "msg": "New status message"})
  msg = {'status': 400, 'message': msg + '. Ex: ' + ex}
  resp = jsonify(msg)
  resp.status_code = 400

  return resp

# Invalid URI handler
@app.errorhandler(404)
def not_found(error=None):
  msg = {'status': 404, 'message': 'Invalid URI. ex: http://hostname.domain:1987/way',}
  resp = jsonify(msg)
  resp.status_code = 404

  return resp

# Send to E-Ink display
def display(Name, Status):
  EPD_WIDTH = 640
  EPD_HEIGHT = 384
  w = 255
  b = 0
  r = 127
  fontPath = '/fonts/Roboto-Bold.ttf'
  epd = epd7in5b.EPD()
  epd.init()

  # For simplicity, the arguments are explicit numerical coordinates
  image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), w)    # 255: clear the frame, white background
  draw = ImageDraw.Draw(image)
  font = ImageFont.truetype(fontPath, 40)
  font2 = ImageFont.truetype(fontPath, 30)
  Nx,Nh = font.getsize(Name)
  draw.text(((EPD_WIDTH-Nx)/2, 100), Name, font=font, fill=b)
  Sx,Sh = font2.getsize(Status)
  draw.text(((EPD_WIDTH-Sx)/2, 200), Status, font=font2, fill=r)
  epd.display_frame(epd.get_frame_buffer(image))



if __name__ == "__main__":
    # Run the flask server
    app.run(host='0.0.0.0', port=8080, threaded=True)
