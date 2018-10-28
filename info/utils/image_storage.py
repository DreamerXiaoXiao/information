from qiniu import Auth, put_data

access_key = "4HBIql9eAsPACfH6ziOyvFdnZZvGLs3PzF9ilJso"
secret_key = "l7bo5yfJjZ2uE5dzBLNImce1kVeH1TlAJeS4ATOe"
bucket_name = "dreamer"


def storage(data):
    try:
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = put_data(token, None, data)
        print(ret, info)
    except Exception as e:
        raise e;

    if info.status_code != 200:
        raise Exception("上传图片失败")
    return ret["key"]


if __name__ == '__main__':
    with open('1.jpg', 'rb') as f:
        storage(f.read())