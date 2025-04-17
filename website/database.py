import pandas as pd
import os

# 현재 파일이 위치한 경로 기준으로 database.csv 경로 설정
current_path = os.path.dirname(__file__)
csv_path = os.path.join(current_path, "database.csv")
static_path = os.path.join(current_path, "static")


def save(title, content, nickname):
    print("📂 CSV 저장 경로:", csv_path)
    print("✅ save() 함수 호출됨!")

    # 파일 없으면 새로 생성
    if not os.path.exists(csv_path):
        df = pd.DataFrame(columns=["title", "content", "nickname"])
        df.to_csv(csv_path, index=False)

    # 기존 데이터 읽고 새 데이터 추가
    df = pd.read_csv(csv_path)
    idx = len(df)

    new_df = pd.DataFrame({
        "title": [title],
        "content": [content],
        "nickname": [nickname]
    })

    new_df.to_csv(csv_path, mode="a", header=False, index=False)
    print("✅ 데이터 저장 완료!")


def load_list():
    if not os.path.exists(csv_path):
        return []
    df = pd.read_csv(csv_path)
    return df.values.tolist()


def now_index():
    if not os.path.exists(csv_path):
        return 0
    df = pd.read_csv(csv_path)
    return len(df) - 1


def load_board(idx):
    if not os.path.exists(csv_path):
        return {"title": "N/A", "content": "N/A", "nickname": "N/A"}

    df = pd.read_csv(csv_path)
    if idx < 0 or idx >= len(df):
        return {"title": "Invalid", "content": "Index out of range", "nickname": ""}
    
    return df.iloc[idx]

def update_post(index, new_title, new_content):
    df = pd.read_csv(csv_path)
    df.at[index, 'title'] = new_title
    df.at[index, 'content'] = new_content
    df.to_csv(csv_path, index=False)

def delete_post(index):
    df = pd.read_csv(csv_path)
    df = df.drop(index)
    df.reset_index(drop=True, inplace=True)
    df.to_csv(csv_path, index=False)

    # 게시글 이미지도 삭제 (선택 사항)
    image_path = os.path.join(static_path, f"{index}.jpeg")
    if os.path.exists(image_path):
        os.remove(image_path)
