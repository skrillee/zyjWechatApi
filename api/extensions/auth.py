import jwt
from jwt import exceptions
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JwtQueryParamsAuthentication(BaseAuthentication):

    def perform_authentication(self, request):
        """
        重写父类的用户验证方法，不在进入视图前就检查JWT
        """
        pass

    def authenticate(self, request):
        token = request.query_params.get('token')
        salt = settings.SECRET_KEY
        try:
            payload = jwt.decode(token, salt, algorithms=['HS256'])
        except exceptions.ExpiredSignatureError:
            raise AuthenticationFailed({'code': 1003, 'error': "token已经失效"})
        except jwt.DecodeError:
            raise AuthenticationFailed({'code': 1003, 'error': "token认证失败"})
        except jwt.InvalidTokenError:
            raise AuthenticationFailed({'code': 1003, 'error': "非法的token"})
        return payload, token

    # 三种操作：
    # 抛出异常，抛出异常后，view中后面的程序就不再进行，页面就看到异常
    # return 一个元组，表示认证通过，以后在视图中条用request.user就是元祖的第一个值，request.auth就是元组的第二个值。
    # 返回一个None，什么都不管，进行下一次的认证。
