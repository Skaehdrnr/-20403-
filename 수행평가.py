import os
import pickle
import datetime
import google.auth
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

tasks = []

def add_task(task, deadline):
    # 할일을 추가하는 함수
    tasks.append((task, deadline))
    print("할일이 추가되었습니다.")

def remove_task(task):
    # 할일을 삭제하는 함수
    for t, _ in tasks:
        if t == task:
            tasks.remove((t, _))
            print("할일이 삭제되었습니다.")
            return
    print("찾을 수 없는 할일입니다.")

def view_tasks():
    if len(tasks) > 0:
        # 할일 목록이 있는 경우 출력
        print("할일 목록:")
        for task, deadline in tasks:
            print("- {} (제출 기한: {})".format(task, deadline.strftime("%Y-%m-%d %H:%M")))
    else:
        # 할일 목록이 없는 경우 메시지 출력
        print("할일이 없습니다.")

def fetch_assignments():
    # Google Classroom에서 과제 정보를 가져와 할일로 추가하는 함수
    creds = None
    token_pickle_file = "token.pickle"
    credentials_json_file = "credentials.json"
    api_service_name = "classroom"
    api_version = "v1"
    scopes = ["https://www.googleapis.com/auth/classroom.courses.readonly", "https://www.googleapis.com/auth/classroom.coursework.me.readonly"]

    if os.path.exists(token_pickle_file):
        # 토큰 파일이 이미 존재하는 경우, 저장된 토큰 로드
        with open(token_pickle_file, "rb") as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        # 유효한 인증 정보가 없는 경우, 새로운 인증 정보 생성
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google.auth.default(scopes=scopes)
            creds = flow.run_local_server(port=0)
        # 생성된 인증 정보를 토큰 파일에 저장
        with open(token_pickle_file, "wb") as token:
            pickle.dump(creds, token)
    
    # Google Classroom 서비스 생성
    service = build(api_service_name, api_version, credentials=creds)

    # 과정 목록 가져오기
    courses = service.courses().list().execute().get("courses", [])
    now = datetime.datetime.utcnow().isoformat() + "Z"
    for course in courses:
        course_id = course["id"]
        course_name = course["name"]
        # 해당 과정의 과제 목록 가져오기
        assignments = service.courses().courseWork().list(courseId=course_id, orderBy="dueDate", pageSize=10).execute().get("courseWork", [])
        for assignment in assignments:
            task = assignment["title"]
            deadline_str = assignment["dueDate"]
            deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M:%SZ")
            # 가져온 과제를 할일로 추가
            add_task("[{}] {}".format(course_name, task), deadline)

def main():
    print("간단한 할일 관리 애플리케이션입니다.")
    while True:
        print("\n명령을 선택하세요:")
        print("1. 할일 추가")
        print("2. 할일 삭제")
        print("3. 할일 목록 보기")
        print("4. 클래스룸에서 과제 가져오기")
        print("5. 종료")

        choice = input("선택: ")

        if choice == "1":
            # 사용자로부터 할일 정보 입력 받기
            task = input("추가할 할일을 입력하세요: ")
            deadline_str = input("제출 기한을 입력하세요 (YYYY-MM-DD HH:MM 형식): ")
            try:
                # 날짜 형식 변환하여 할일 추가
                deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
                add_task(task, deadline)
            except ValueError:
                print("올바른 날짜 형식을 입력하세요.")
        elif choice == "2":
            # 사용자로부터 삭제할 할일 정보 입력 받기
            task = input("삭제할 할일을 입력하세요: ")
            remove_task(task)
        elif choice == "3":
            # 할일 목록 보기
            view_tasks()
        elif choice == "4":
            # Google Classroom에서 과제 정보 가져오기
            fetch_assignments()
            print("과제 정보가 클래스룸에서 가져와져서 앱에 저장되었습니다.")
        elif choice == "5":
            print("프로그램을 종료합니다.")
            break
        else:
            print("유효하지 않은 선택입니다.")

if __name__ == "__main__":
    main()
