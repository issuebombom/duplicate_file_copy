# CLI 환경을 동원해서 파일 복사

import os
import re

# Raw 폴더 경로 가져오기
RAW_FOLDER_PATH = "/Users/leitmotiv/Desktop/test/photo_test_folder/raw"
# Selected 폴더 경로 가져오기
SELECTED_FOLDER_PATH = "/Users/leitmotiv/Desktop/test/photo_test_folder/selected"
# Selected 사진 파일 확장명
SELETED_IMAGE_EXTENTIONS = ['.jpg', '.png']
# Raw 사진 파일 확장명(xmp 포함)
RAW_IMAGE_EXTENTIONS = ['.arw', '.cr2', '.xmp']


"""폴더 내 폴더 및 파일명 정보를 dictionary 형태로 출력합니다.
"""
def get_file_info(path, extentions):
    """지정한 디렉토리 내  폴더와 하위 파일에 대한 정보를 dictionary 형태로 출력합니다.

    Args:
        path (str): directory
        extentions (list): 확장자 정보가 담긴 리스트

    Returns:
        dict: {폴더명: {파일명1, 파일명2, 파일명3...}}
    """

    os.chdir(path)

    # 셀렉 폴더명 수집
    folder_name_list = os.popen("ls | grep -v '*.*'").read().split()

    # grep 명령어에 맞게 수정
    extentions = '|'.join(extentions)

    # 폴더명 내 jpg 파일명 리스트 가져오기 (확장자 제거)
    file_info = {} # {폴더명: {파일명1, 파일명2, 파일명3...}}
    for folder_name in folder_name_list: # 폴더명을 순차적으로 출력
        subpath = f"{path}/{folder_name}" # 하위 폴더로 이동
        cli_cmd_result = os.popen(f"ls {subpath} | grep -iE '{extentions}'").read() # 해당하는 확장자 파일 목록 로드
        filename_list = re.sub('\.\w+[\n\t\r]', ' ', cli_cmd_result).split() # 파일명 추출(확장자, 공백, 특수기호 제거)
        file_info[folder_name] = filename_list
    
    return file_info


def caution_check(selected_info, raw_info):
    """예외처리

    Args:
        selected_info (dict): 셀렉 폴더에 대한 정보
        raw_info (dict): 원본 폴더에 대한 정보

    Raises:
        Exception: 셀렉 폴더의 하위폴더가 원본 폴더에 존재 유무 체크
        Exception: 원본 파일에 존재하지 않는 셀렉 파일명의 존재 유무 체크
    """

    # 셀렉 폴더 존재 유무 체크
    duplicate_list = set(selected_info.keys()) & set(raw_info.keys())

    if len(duplicate_list) != 0:
        raise Exception(f"{duplicate_list} 폴더가 원본 폴더 내 존재합니다.")
    
    # 원본 파일명에서 찾을 수 없는 셀렉 파일명 체크
    folder_name_list = list(selected_info.keys())
    for folder in folder_name_list:
        faw_file_list = sum(list(raw_info.values()), [])
        # 셀렉 파일과 원본 파일의 차집합을 구합니다.
        cant_find_list = set(selected_info[folder]) - set(faw_file_list)

        if len(cant_find_list) != 0:
            raise Exception(f"{folder} 폴더의 {cant_find_list}를 원본에서 찾을 수 없습니다.")


def run(raw_folder_path, selected_folder_path, raw_extentions, selected_extentions):
    """셀렉 폴더 내 파일명과 일치하는 원본 파일 탐색 후 복사
        ex) 셀렉폴더의 a.jpg 파일명과 일치하는 원본 파일 a.arw를 찾아서 따로 복사해 둡니다.

    Args:
        raw_folder_path (str): 원본 폴더 경로
        selected_folder_path (str): 셀렉 폴더 경로
        raw_extentions (list): 원본 파일 확장자 리스트
        selected_extentions (list): 셀렉 파일 확장자 리스트
    """

    selected_info = get_file_info(selected_folder_path, selected_extentions)
    raw_info = get_file_info(raw_folder_path, raw_extentions)
    caution_check(selected_info, raw_info)

    os.chdir(RAW_FOLDER_PATH)
    copy_info = {} # {폴더명: ["복사경로1, 복사경로2, 복사경로3, ..."]}
    for folder, files in selected_info.items(): # selected_info를 활용해서 동일 파일명 탐색
        files = list(map(lambda x: x+".*", files)) # 파일명 뒤에 .* 달기
        cond1 = '|'.join(files) # 파일명.*|파일명.*|파일명.*
        cond2 = '|'.join(RAW_IMAGE_EXTENTIONS) # .arw|.cr2|.xmp
        copy_path_list = os.popen(f"find . -type f | grep -E '{cond1}' | grep -iE '{cond2}'").read().split()
        # copy_info[folder] = " ".join(copy_path_list)
        copy_info[folder] = copy_path_list
        
    # 셀렉 폴더명 생성 및 복사
    for folder, files in copy_info.items():
        os.mkdir(folder)
        files = " ".join(files)
        os.popen(f"cp {files} {folder}")

    print("원본 파일의 복사를 완료하였습니다.")


run(RAW_FOLDER_PATH, SELECTED_FOLDER_PATH, RAW_IMAGE_EXTENTIONS, SELETED_IMAGE_EXTENTIONS)