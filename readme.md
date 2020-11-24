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
  
  
### 6. 슈퍼유저
/admin으로 어드민 페이지 접속
```
ID : super
PW : tbvjdbwj (슈퍼유저 영타에서 그대로 입력)
```

# 실행 방법 for Windows 10

## 환경 설정

1. Python 3 설치

1. 필요한 Python 라이브러리 설치
    1. pip install `django`
    1. pip install `djangorestframework`
    1. pip install `django-cors-headers`
    1. pip install `pymysql`

1. MySQL [다운로드](https://dev.mysql.com/downloads/installer/)하여 설치
    1. Terminal에서 `mysql` 프로그램을 바로 실행할 수 있도록 환경변수 등 준비
    1. 서버에서는 user name이 `dgucovid`이고 비밀번호가 `COVID@dgu2020`인 계정을 사용하므로 지금 만들어야 함
    1. Terminal을 열어서 다음 명령어들을 입력하여 계정 추가
        1. `mysql -u root -p`
        1. MySQL 설치할 때 설정한 root 계정의 비밀번호 입력
        1. `CREATE USER 'dgucovid'@'localhost' IDENTIFIED BY 'COVID@dgu2020';`
        1. `GRANT ALL PRIVILEGES ON *.* TO 'dgucovid'@'localhost';`
        1. `FLUSH PRIVILEGES;`

1. BLAST+
    1. Windows의 경우
        * [이곳](https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/)에서 버전에 맞는 installer를 다운로드
        * bin 폴더 위치를 찾아 환경변수의 path에 추가
        * 기본값 : `C:\Program Files\NCBI\blast-2.10.1+\bin`
        * 환경변수 `BLASTDB_LMDB_MAP_SIZE`를 추가하여 값을 1000000으로 설정
    1. Linux의 경우
        * `sudo apt install ncbi-blast+`
    1. `makeblastdb -version`, `blastn -version` 두 명령어를 terminal에 입력하여 제대로 설치되었나 확인

1. Muscle
    1. Windows의 경우
        * [이곳](https://www.drive5.com/muscle/downloads.htm)에서 exe 파일을 다운로드한 뒤, 그 파일이 terminal에서 `muscle` 명령어만으로 실행될 수 있도록 세팅해야 됨
        * 가장 편한 방법은 파일 이름을 바꾼 뒤 레포 루트 폴더에 넣는 것
    1. Linux의 경우
        * `sudo apt install muscle`
    1. `muscle -version` 명령어를 입력하여 제대로 설치되었나 확인

1. 깃 레포지토리 클론
    1. 서브모듈도 다운로드 해야 하기 때문에 아래와 같은 명령어로 클론
    1. `git clone --recurse-submodules -j8 https://github.com/hayunyun/DGU2020_COVID_back`
    1. 클론이 완료된 레포지토리 폴더 안에서 terminal을 열어 `python manage.py runserver`이 되나 테스트한 후 `Ctrl+C`로 종료

## 데이터베이스 생성

1. 필요한 파일 준비
    1. 압축파일 `{repo}/extern/DGU2020_covid_database/database/sequences_2020-11-13_07-24.fasta.gz.xz`를 찾아 압축 해제하여 `sequences.fasta` 파일을 `database` 폴더 안에 배치
    1. 압축파일 `{repo}/extern/DGU2020_covid_database/database/metadata_2020-11-13_07-22.tsv.gz`를 찾아 압축 해제하여 `metadata.tsv` 파일을 `database` 폴더 안에 배치

1. BLAST
    1. 레포지토리 루트 폴더에서 terminal을 실행하여 `python manage.py gen_blast_db "./extern/DGU2020_covid_database/database"`를 실행
    1. `generated blast db successfully`라고 뜨면 성공한 것

1. MySQL
    1. 레포지토리 루트 폴더에서 terminal을 실행하여 `python manage.py populate_mysql_db "./extern/DGU2020_covid_database/database"` 명령어 실행

## 서버 실행

1. `python manage.py runserver`
1. 웹브라우저를 열어 주소창에 `localhost:8000/api/echo/` 입력
1. 텍스트를 입력할 수 있는 페이지가 뜨면 성공
