1. Upload.js (mia-react-app\src\component\pages\UploadPage\Upload.js)
2. views.py ( projectMIA\mia\views.py )

Upload.js에서 profile_url과 img_name 출력해 봤는데 잘 되더라구욥,,!

그래서 이거를 json 파일로 만들어서 보내서 (upload 버튼을 만들어놓았고 사진 선택후 upload 버튼 누르면 post !)
views.py에서는, json파일 받아와 이용하면 되지 않을까 하는 생각입니다,,!

지금 views.py에서는 리액트에서 생성된 주소 직접 넣어주었구, 돌아가는거는 확인했숩니당
그래서 url 받아온거 쓰구, img_name은 저장할 때 이름으로 넣으려구요,,!

용량이 너무커서,, 이 둘만 올립니당 ㅠ ㅠ 감사합니당 ㅠㅠㅠㅠㅠㅠ

+ endpoint : `/api/v1/mia/img`
