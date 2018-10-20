from flask import request, abort, make_response

from info import redis_store
from info.utils.captcha.captcha import captcha
from . import passport_blu


@passport_blu.route('/image_code')
def get_image_code():
    """
       生成图片验证码并返回
       1. 取到参数
       2. 判断参数是否有值
       3. 生成图片验证码
       4. 保存图片验证码文字内容到redis
       5. 返回验证码图片
    """
    image_code_id = request.args.get('imageCodeId', None)

    if not image_code_id:
        abort(403)

    name, text, image = captcha.generate_captcha()

    redis_store.setex("image_code" + image_code_id, 300, text)

    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'
    return response


