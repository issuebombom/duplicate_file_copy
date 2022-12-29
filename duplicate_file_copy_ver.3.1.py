import os
import shutil
from tkinter import *
import tkinter.ttk as ttk
import tkinter.font as tkFont
import tkinter.messagebox as msgbox
from tkinter import filedialog
from functools import partial


class Path:
    """엔트리에서 경로정보를 받는 부모클래스"""
    def __init__(self, raw_path, selected_path):
        self.raw_path = raw_path.get()
        self.selected_path = selected_path.get()


class Tool(Path):
    """프로젝트 수행 단계에서 필요한 기능 클래스"""
    def __init__(self, raw_path, selected_path):
        super().__init__(raw_path, selected_path)

    def caution_msg(self):
        """경고 문구창 팝업에 대한 함수"""
        
        # 셀렉폴더 내 폴더와 같은 이름의 폴더가 원본폴더 내 존재할 경우                
        if len(self.raw_path) == 0:
            msgbox.showwarning("경고", "원본폴더 경로를 선택하세요")
            return

        elif len(self.selected_path) == 0:
            msgbox.showwarning("경고", "셀렉폴더 경로를 선택하세요")
            return

        # 올바른 경로 지정 확인
        elif os.path.isdir(self.raw_path) + os.path.isdir(self.selected_path) != 2:
            msgbox.showwarning("경고", "존재하지 않는 경로입니다.")
            return

        # 원본 폴더에 새폴더 생성 단계에서 같은 폴더가 이미 존재할 경우에 대한 차단장치
        for folder_name in os.listdir(self.raw_path):
            if folder_name.startswith('.') == True:
                continue
            elif folder_name in os.listdir(self.selected_path):
                msgbox.showwarning("경고", f"지정한 원본폴더 내 셀렉폴더명과 중복된 이름의 폴더가 존재합니다. 원본폴더에서 해당 폴더를 삭제하세요. \n[중복 폴더 이름: {folder_name}]")
                return
        
        return "OK"

    def get_folder_dir(self, path, get_name=False):
        """하위 폴더 디렉토리(또는 파일명) 정보를 리스트로 저장한다."""
        folder_dir_list = []
        for name in os.listdir(path):
            if os.path.isdir(os.path.join(path, name)) == True:
                if get_name == False:
                    folder_dir_list.append(os.path.join(path, name)) # 파일 경로 다 가져오기
                if get_name == True:
                    folder_dir_list.append(name) # 파일명만 가져오기
        
        return folder_dir_list
    
    def get_file_dir(self, path, get_name=False):
        """하위 파일 디렉토리(또는 파일명) 정보를 리스트로 저장한다."""
        file_dir_list = []
        for name in os.listdir(path):
            if name.startswith(".") == True: # 숨김파일 제외, Thumbs 파일 제외
                continue
            elif name == "Thumbs.db":
                continue
            elif os.path.isfile(os.path.join(path, name)) == True:
                if get_name == False:
                    file_dir_list.append(os.path.join(path, name)) # 파일 경로 다 가져오기
                if get_name == True:
                    file_dir_list.append(name) # 파일명만 가져오기
        
        return file_dir_list
    
    def get_folder_name(self, folder_path):
        """지정 경로의 폴더 이름을 리턴"""
        return os.path.split(folder_path)[1]
    
    def get_file_name(self, file_or_path):
        """지정 경로의 파일 이름(확장자 제외)을 리턴"""
        return os.path.splitext(os.path.split(file_or_path)[1])[0]
    
    def get_ext_name(self, file_or_path):
        """지정 경로의 확장자 이름을 리턴"""
        return os.path.splitext(file_or_path)[1]
    
    def check_dir_empty(self, path):
        """지정 디렉토리가 숨김파일을 제외하고 비었는지 체크"""
        for name in os.listdir(path):
            if name.startswith(".") == False:
                return False

        return True            


class Match(Tool):
    """동일명 파일(확장자 제외)을 매칭 후 복사하는 클래스"""
    def __init__(self, raw_path, selected_path):
        super().__init__(raw_path, selected_path)

        self.selected_path_dict = {}
        self.raw_path_dict = {}
        self.raw_ext_set = set() # extension(확장자)
        self.raw_filename_set = set()

        self.results = [] # 폴더별 복사한 파일 수
        self.not_found_set = set() # 찾지 못한 파일 목록


    def get_selec_filename_to_dict(self, path=None):
        """셀렉 디렉토리 내 폴더명과 파일명 정보를 dict로 가져온다."""
        # {'A컷': ['d.jpg', 'e.jpg']}
        
        if path == None:
            path = self.selected_path

        for folder_dir in self.get_folder_dir(path):
            # 빈 폴더는 경로 정보를 가져오지 않는다.
            if self.check_dir_empty(folder_dir) == False:
                # 폴더 이름 추출
                folder_name = self.get_folder_name(folder_dir)
                # {"폴더 이름": [파일 이름 리스트]}
                self.selected_path_dict[folder_name] = self.get_file_dir(folder_dir, get_name=True)
                # 재귀
                self.get_selec_filename_to_dict(folder_dir)



    def get_raw_dir_to_dict(self, path=None):
        """원본 디렉토리 내 파일명과 파일 경로 정보를 dict로 가져온다."""
        # {'b.ARW': '/Users/leitmotiv/Desktop/raw/bb/b.ARW'}
        if path == None:
            path = self.raw_path

        for folder_dir in self.get_folder_dir(path):
            # jpg 이름을 가진 폴더는 가져오지 않는다.(해당 사례가 늘 존재해서 걸어둔 장치)
            if folder_dir == "jpg":
                continue
            # 빈 폴더는 경로 정보를 가져오지 않는다.
            elif self.check_dir_empty(folder_dir) == False:
                # 파일 이름 추출
                for file_dir in self.get_file_dir(folder_dir, get_name=True):
                    # jpg 파일은 무시하기
                    if self.get_ext_name(file_dir) in [".jpg", ".JPG", '.zip']:
                        continue
                    else:
                        # {"파일명": "파일 경로"}
                        self.raw_path_dict[file_dir] = os.path.join(folder_dir, file_dir)
                        # 파일명(확장자 제외) 보관
                        self.raw_filename_set.add(self.get_file_name(file_dir))
                        # raw파일 확장자 가져오기
                        self.raw_ext_set.add(self.get_ext_name(file_dir))
                # 재귀
                self.get_raw_dir_to_dict(folder_dir)


    def match_files(self):
        """셀렉본을 기준으로 원본 파일 복사"""
        
        # 원본 폴더에 대한 처리
        for folder_name in self.selected_path_dict.keys():
            moved_file_count = 0
            # 새폴더 생성
            new_dir = os.path.join(self.raw_path, folder_name)
            os.mkdir(new_dir)

            for file_name in self.selected_path_dict[folder_name]:
                for raw_ext in self.raw_ext_set:
                    name_without_ext = self.get_file_name(file_name)
                    look_for = name_without_ext + raw_ext

                    try:
                        shutil.copy(self.raw_path_dict[look_for], new_dir)
                        moved_file_count += 1
                    except:
                        if name_without_ext in self.raw_filename_set:
                            continue
                        else: 
                            self.not_found_set.add(name_without_ext)
                            continue

            self.results.append(f"{folder_name}: {moved_file_count}")

        return self.results

    def result(self):
        """실행결과 출력"""
        msgbox.showinfo("알림", "작업이 완료되었습니다.")

        combobox1['values'] = self.results

        if len(self.not_found_set) == 0:
            combobox2['values'] = 0
        else:
            combobox2['values'] = self.not_found_set
  

def start():
    """코드 실행"""
    match = Match(raw_path, selected_path)

    if match.caution_msg() == "OK": 
        # match.loading_start()
        match.get_selec_filename_to_dict()
        match.get_raw_dir_to_dict()
        match.match_files()
        # match.loading_end()
        match.result()
    else:
        return

def select_dir(entry):
    """경로를 지정하면 해당 엔트리에 넘겨줍니다."""
    loc_path = filedialog.askdirectory()

    if loc_path == '':
        return

    entry.delete(0, END)
    entry.insert(0, loc_path)


# Window 틀 만들기
root = Tk()
root.title("photo_classifier ver. 3.1") # 창 이름 설정
root.geometry('320x450') # 창 크기 가로크기 x 세로크기 + x좌표 + y좌표
root.resizable(False, False) # x너비, y너비 (창 크기 변경 허용유무)

# Window 구성
frame_path1 = LabelFrame(root, text='원본폴더모음 경로')
frame_path1.pack(fill='x', padx=5, pady=5)

Label(frame_path1, text='※ 원본사진폴더들이 담긴 경로를 선택하세요').pack(pady=5)

raw_path = Entry(frame_path1, width=22)
raw_path.pack(side='left', fill='x', expand=True)

btn_path = Button(frame_path1, text="찾아보기", width=7, command=partial(select_dir, raw_path))
btn_path.pack(side='right', padx=5)

frame_path2 = LabelFrame(root, text='셀렉폴더모음 경로')
frame_path2.pack(fill='x', padx=5, pady=5)

Label(frame_path2, text='※ 셀렉사진폴더들이 담긴 경로를 선택하세요').pack(pady=5)

selected_path = Entry(frame_path2, width=22)
selected_path.pack(side='left', fill='x', expand=True)

btn_path = Button(frame_path2, text="찾아보기", width=7, command=partial(select_dir, selected_path))
btn_path.pack(side='right', padx=5)

frame_result1 = LabelFrame(root, text='결과')
frame_result1.pack(fill='x', padx=5, pady=10)

combobox1 = ttk.Combobox(frame_result1, height=5, values=[], state='readonly')
combobox1.pack(pady=5)
combobox1.set('복사한 파일 개수') # 콤보박스 default 보기 값

combobox2 = ttk.Combobox(frame_result1, height=5, values=[], state='readonly')
combobox2.pack(pady=5)
combobox2.set('찾지 못한 파일') # 콤보박스 default 보기 값

font = tkFont.Font(family="Rockwell", size=8)
Label(root, text='Copyright 2021 Parkminyoung All rights reserved.', font=font).pack(side='bottom', pady=5)


btn = Button(root, text='시작', command=start)
btn.pack()

root.mainloop()