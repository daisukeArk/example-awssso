from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils


def init_saml_auth(params):
    """SAMLクライアント初期化

    クライアント初期化パラメータ、saml/settings.json・saml/advanced_settings.json ファイルで初期化を行う
    """
    auth = OneLogin_Saml2_Auth(params, custom_base_path=settings.SAML_FOLDER)
    return auth


def prepare_django_request(request):
    """SAMLクライアント初期化パラメータ取得

    HTTPリクエストオブジェクトからSAMLクライアント初期化パラメータを生成する
    """
    params = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'server_port': request.META['SERVER_PORT'],
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy()
    }
    return params


def index(request):
    """TOPページ表示

    TOPページをレンダリングする
    """

    # コンテキストパラメータ初期化
    attributes = False

    if 'samlUserdata' in request.session:
        if len(request.session['samlUserdata']) > 0:
            attributes = request.session['samlUserdata'].items()

    return render(request, 'index.html', { 'attributes': attributes, })


@csrf_exempt
def sso(request):
    """AWS SSOリダイレクト

    AWS SSOへリダイレクトする
    """

    # 初期化パラメータ取得
    prepare_params = prepare_django_request(request)
    # 初期化
    auth = init_saml_auth(prepare_params)

    return HttpResponseRedirect(auth.login())


@csrf_exempt
def acs(request):
    """アサーション検証

    ユーザーがアプリケーションへのアクセス許可されているかを検証する
    """

    # 初期化パラメータ取得
    prepare_params = prepare_django_request(request)
    # 初期化
    auth = init_saml_auth(prepare_params)

    request_id = None
    if 'AuthNRequestID' in request.session:
        request_id = request.session['AuthNRequestID']

    auth.process_response(request_id=request_id)
    errors = auth.get_errors()

    if not errors:
        if 'AuthNRequestID' in request.session:
            del request.session['AuthNRequestID']
        request.session['samlUserdata'] = auth.get_attributes()
        request.session['samlNameId'] = auth.get_nameid()
        request.session['samlNameIdFormat'] = auth.get_nameid_format()
        request.session['samlNameIdNameQualifier'] = auth.get_nameid_nq()
        request.session['samlNameIdSPNameQualifier'] = auth.get_nameid_spnq()
        request.session['samlSessionIndex'] = auth.get_session_index()

    return HttpResponseRedirect(auth.redirect_to('/'))


def metadata(request):
    """SPメタデータ表示

    メタデータを出力する
    """
    saml_settings = OneLogin_Saml2_Settings(settings=None, custom_base_path=settings.SAML_FOLDER, sp_validation_only=True)
    metadata = saml_settings.get_sp_metadata()
    errors = saml_settings.validate_metadata(metadata)

    if len(errors) == 0:
        return HttpResponse(content=metadata, content_type='text/xml')
    else:
        return HttpResponseServerError(content=', '.join(errors))
