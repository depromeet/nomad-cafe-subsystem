## nomad-cafe-subsystem
노마드 카페 서버 구동 시 필요한 서브시스템

### 버전 정보

- python : 3.8.x
- certifi	: 2020.6.20
- chardet	: 3.0.4
- configparser : 	5.0.0
- dnspython	: 2.0.0
- idna	: 2.10
- pip	: 20.2
- pymongo	: 3.10.1
- requests : 2.24.0
- setuptools : 	49.2.0
- urllib3 : 1.25.10

### mongodb 설정
mongo Atlas 연결을 위해서는 mongo+srv scheme을 사용한다. 이로 인해 dnspython 모듈 설치가 필요하다.
```
pip3 install dnspython
```
dnspython 1.15버전에서는 mongodb 접속 시 아래와 같은 오류가 발생하므로 1.16 이상 버전으로 설치해야한다.
```
pymongo.errors.ConfigurationError: query() got an unexpected keyword argument 'lifetime'
```
주변 지역 탐색 쿼리를 위해 아래 명령으로 인덱스를 활성화해야함
```
db.cafe.ensureIndex({location:"2dsphere"})
```

### 로컬에서 데이터베이스 접속 (on Windows)
1. mongo Shell Download
    ```
    https://downloads.mongodb.org/win32/mongodb-shell-win32-x86_64-2012plus-4.2.8.zip
    ```
2. mongo Shell에서 연결
    ```
    mongo "mongodb+srv://nomad-cafe.kgqub.mongodb.net/<dbname>" --username <username>
    ```
    - dbname : nomad-cafe
    - username : nomad-cafe
    
### AWS CDK로 프로비저닝
1. cdk 경로로 이동
    ```buildoutcfg
    cd aws_cdk
    ```
2. setup
    ```buildoutcfg
    python3 setup.py install
    ```
3. cdk 실행
    ```buildoutcfg
    cdk deploy VpcCdkStack Ec2CdkStack SgCdkStack
    ```