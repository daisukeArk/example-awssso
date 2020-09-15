# example-awssso

## 前提条件や動作環境

- macOS 10.15.6
- Python 3.7.8
- Django 3.1.1
- python3-saml 1.9.0
- django-sslserver 0.22

## セットアップ

```Shell
# 仮想環境の作成
$ python -m venv ~/envs/example-awssso

# 起動
$ source ~/envs/example-awssso/bin/activate
```

## インストール、プロジェクト作成

```Shell
# Django インストール
(example-awssso) $ python -m pip install Django

# バージョン確認
(example-awssso) $ python -m django --version
3.1.1

# プロジェクト作成
(example-awssso) $ django-admin startproject webapp .
```

## インストール(ssl)

`開発用`です。SSL通信を許可します。くれぐれも本番環境では利用しないようにしてください。
自己証明書作成については割愛します。

```Shell
(example-awssso) $ pip install django-sslserver
```

## インストール(python3-saml)

SAML認証サポートには色々ありましたが、`python3-saml`を試してみることにしました。</br>
`python3-saml`のインストール前に`xmlsec`の依存解決をします。

[https://github.com/onelogin/python3-saml](https://github.com/onelogin/python3-saml)
[https://pypi.org/project/xmlsec/](https://pypi.org/project/xmlsec/)

```Shell
# xmlsec 依存関係解決
(example-awssso) $ brew install libxml2 libxmlsec1 pkg-config

# インストール
(example-awssso) $ pip install python3-saml
```

## アプリケーションセットアップ

python3-samlのGitHubにDjangoのサンプルコードがあるのでそちらも参考にしてください。

```Shell
(example-awssso) $ mkdir saml

# 設定用の空ファイルを作成
(example-awssso) $ touch saml/settings.json
(example-awssso) $ touch saml/advanced_settings.json
```

### advanced_settings.json

```json
{
  "security": {
    "nameIdEncrypted": false,
    "authnRequestsSigned": false,
    "logoutRequestSigned": false,
    "logoutResponseSigned": false,
    "signMetadata": false,
    "wantMessagesSigned": false,
    "wantAssertionsSigned": false,
    "wantNameId": true,
    "wantNameIdEncrypted": false,
    "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
    "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256"
  },
  "contactPerson": {
    "technical": {
      "givenName": "technical_name",
      "emailAddress": "technical@example.com"
    },
    "support": {
      "givenName": "support_name",
      "emailAddress": "support@example.com"
    }
  },
  "organization": {
    "en-US": {
      "name": "sp_test",
      "displayname": "SP test",
      "url": "https://localhost:8000"
    }
  }
}
```

### settings.json

`AWS SSO SAML メタデータファイル`の内容から以下の設定値を編集して保存します。

#### sp

- entityId
- assertionConsumerService.url
- NameIDFormat

#### idp

`AWS SSO SAML メタデータファイル`の内容から設定してください。

- entityId(entityID)
- singleSignOnService.url(SingleSignOnService.Location)
- singleLogoutService.url(SingleLogoutService.Location)
- x509cert(X509Certificate)

```json
{
  "strict": true,
  "debug": true,
  "sp": {
    "entityId": "https://localhost:8000/metadata/",
    "assertionConsumerService": {
      "url": "https://localhost:8000/acs/",
      "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    },
    "singleLogoutService": {
      "url": "https://localhost:8000/sls/",
      "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    },
    "NameIDFormat": "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
    "x509cert": "",
    "privateKey": ""
  },
  "idp": {
    "entityId": "https://portal.sso.ap-northeast-1.amazonaws.com/saml/assertion/<AWS SSO ID>",
    "singleSignOnService": {
      "url": "https://portal.sso.ap-northeast-1.amazonaws.com/saml/assertion/<AWS SSO ID>",
      "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    },
    "singleLogoutService": {
      "url": "https://portal.sso.ap-northeast-1.amazonaws.com/saml/logout/<AWS SSO ID>",
      "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    },
    "x509cert": "<AWS SSO 証明書>"
  }
}
```
