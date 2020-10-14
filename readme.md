# Django 기본
### 1. 가상환경 생성
```
$ pip install pipenv
$ pipenv shell
```

### 2. 필요한 라이브러리

1. pip install `django`
1. pip install `djangorestframework`
1. pip install `django-cors-headers`

### 3. 프로젝트 생성
  ```
  $ django-admin startproject project이름
  ```


### 4. 앱 생성

  manage.py 파일이 있는 경로로 이동하여
  ```
  $ python manage.py startapp app이름
  ```
  그 다음 상위 경로에서 프로젝트 이름과 같은 폴더로 이동하여 settings.py의 INSTALLED_APPS에 생성한 앱 이름 추가
  
  ```
  INSTALLED_APPS = [
  ...
  'app이름',
  ]
  ```

### 5. 서버 실행

  manage.py 파일이 있는 경로로 이동하여
  `python manage.py runserver` 입력
  
  
