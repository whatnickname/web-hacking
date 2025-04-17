import json
import os
import pandas as pd

comments_file = os.path.join(os.path.dirname(__file__), "comments.json")

# 처음 실행 시 빈 구조 생성
if not os.path.exists(comments_file):
    with open(comments_file, "w", encoding="utf-8") as f:
        json.dump({}, f)

def load_comments(index):
    with open(comments_file, "r", encoding="utf-8") as f:
        all_comments = json.load(f)
    return all_comments.get(str(index), [])

def save_all_comments(all_comments):
    with open(comments_file, "w", encoding="utf-8") as f:
        json.dump(all_comments, f, ensure_ascii=False, indent=2)

def add_comment(index, author, content):
    with open(comments_file, "r", encoding="utf-8") as f:
        all_comments = json.load(f)
    comment_list = all_comments.get(str(index), [])
    comment_id = max([c["id"] for c in comment_list], default=0) + 1
    comment_list.append({"id": comment_id, "author": author, "content": content})
    all_comments[str(index)] = comment_list
    save_all_comments(all_comments)

def edit_comment(comment_id, author, new_content):
    with open(comments_file, "r", encoding="utf-8") as f:
        all_comments = json.load(f)
    for index, comment_list in all_comments.items():
        for comment in comment_list:
            if comment["id"] == comment_id and comment["author"] == author:
                comment["content"] = new_content
                save_all_comments(all_comments)
                return True
    return False

def delete_comment(comment_id, author):
    with open(comments_file, "r", encoding="utf-8") as f:
        all_comments = json.load(f)
    for index, comment_list in all_comments.items():
        for comment in comment_list:
            if comment["id"] == comment_id and comment["author"] == author:
                comment_list.remove(comment)
                all_comments[index] = comment_list
                save_all_comments(all_comments)
                return True
    return False

current_path = os.path.dirname(__file__)
csv_path = os.path.join(current_path, "database.csv")
comments_path = os.path.join(current_path, "comments.csv")

def load_posts():
    return pd.read_csv(csv_path).to_dict("records")

def load_post(index):
    df = pd.read_csv(csv_path)
    return df.iloc[index].to_dict()

def save_post(title, content):
    df = pd.read_csv(csv_path)
    new_row = {"title": title, "content": content}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(csv_path, index=False)

def load_comments(post_id):
    if not os.path.exists(comments_path):
        return []
    df = pd.read_csv(comments_path)
    return df[df['post_id'] == post_id].to_dict("records")

def add_comment(post_id, author, content):
    if os.path.exists(comments_path):
        df = pd.read_csv(comments_path)
    else:
        df = pd.DataFrame(columns=["post_id", "author", "content"])
    new_comment = {"post_id": post_id, "author": author, "content": content}
    df = pd.concat([df, pd.DataFrame([new_comment])], ignore_index=True)
    df.to_csv(comments_path, index=False)