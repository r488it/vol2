from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
import os
import uuid
from datetime import datetime
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーションの初期化
app = FastAPI(
    title="Storybook API",
    description="絵本データ管理API",
    version="1.0.0",
    docs_url=None, 
    redoc_url=None, 
    openapi_url=None
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データディレクトリのパス
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# データディレクトリが存在しない場合は作成
os.makedirs(DATA_DIR, exist_ok=True)

# Pydanticモデル定義
class QuestionData(BaseModel):
    question: str
    answers: List[str]

class PageData(BaseModel):
    pageNumber: int
    text: str
    imagePrompt: str
    imageBase64: str
    audioBase64: str
    questions: Optional[QuestionData] = None

class StorybookMetadata(BaseModel):
    title: str
    createdAt: str
    totalPages: int
    savedPages: int
    skippedPages: int
    version: str
    note: str

class StorybookData(BaseModel):
    metadata: StorybookMetadata
    pages: List[PageData]

class FileListItem(BaseModel):
    filename: str
    title: str
    createdAt: str
    totalPages: int
    savedPages: int
    fileSize: int
    imageBase64: Optional[str] = None

# ルートエンドポイント
@app.get("/")
async def root():
    """
    ルートエンドポイント
    """
    return {"message": "Storybook API Server", "version": "1.0.0"}

# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# JSON アップロードAPI
@app.post("/api/upload-storybook")
async def upload_storybook(storybook_data: StorybookData):
    """
    絵本JSONデータをアップロードして保存する
    """
    try:
        # ファイル名を生成（タイトル + タイムスタンプ + UUID）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id = str(uuid.uuid4())[:8]
        safe_title = "".join(c for c in storybook_data.metadata.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        filename = f"{safe_title}_{timestamp}_{file_id}.json"
        
        # ファイルパス
        file_path = os.path.join(DATA_DIR, filename)
        
        # JSONデータを辞書に変換
        json_data = storybook_data.model_dump()
        
        # ファイルに保存
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # ファイルサイズを取得
        file_size = os.path.getsize(file_path)
        
        logger.info(f"Storybook saved: {filename}, size: {file_size} bytes")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "絵本データが正常に保存されました",
                "filename": filename,
                "file_size": file_size,
                "saved_pages": storybook_data.metadata.savedPages,
                "total_pages": storybook_data.metadata.totalPages
            }
        )
        
    except Exception as e:
        logger.error(f"Error saving storybook: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"ファイルの保存中にエラーが発生しました: {str(e)}"
        )

# ファイル一覧取得API
@app.get("/api/storybooks", response_model=List[FileListItem])
async def get_storybook_list():
    """
    保存されている絵本ファイルの一覧を取得する
    各絵本のメタデータ情報とページ1のimageBase64データを含む
    """
    try:
        file_list = []
        
        # dataディレクトリ内のJSONファイルを検索
        if os.path.exists(DATA_DIR):
            for filename in os.listdir(DATA_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(DATA_DIR, filename)
                    
                    try:
                        # ファイルサイズを取得
                        file_size = os.path.getsize(file_path)
                        
                        # JSONファイルを読み込んでメタデータを取得
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # メタデータが存在することを確認
                        if 'metadata' in data:
                            metadata = data['metadata']
                            
                            # ページ1のimageBase64を取得
                            page1_image = None
                            if 'pages' in data and isinstance(data['pages'], list):
                                # pageNumber=1のページを検索
                                for page in data['pages']:
                                    if isinstance(page, dict) and page.get('pageNumber') == 1:
                                        page1_image = page.get('imageBase64')
                                        break
                            
                            file_info = FileListItem(
                                filename=filename,
                                title=metadata.get('title', 'タイトル不明'),
                                createdAt=metadata.get('createdAt', ''),
                                totalPages=metadata.get('totalPages', 0),
                                savedPages=metadata.get('savedPages', 0),
                                fileSize=file_size,
                                imageBase64=page1_image
                            )
                            file_list.append(file_info)
                        else:
                            logger.warning(f"File {filename} does not contain metadata")
                            
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        logger.warning(f"Error reading file {filename}: {str(e)}")
                        continue
        
        # 作成日時でソート（新しい順）
        file_list.sort(key=lambda x: x.createdAt, reverse=True)
        
        logger.info(f"Found {len(file_list)} storybook files")
        return file_list
        
    except Exception as e:
        logger.error(f"Error getting storybook list: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"ファイル一覧の取得中にエラーが発生しました: {str(e)}"
        )

# 個別絵本データ取得API
@app.get("/api/storybook/{filename}", response_model=StorybookData)
async def get_storybook_by_filename(filename: str):
    """
    指定されたファイル名の絵本データを取得する
    """
    try:
        # ファイル名のセキュリティチェック
        # パストラバーサル攻撃防止のため、ファイル名に特定の文字が含まれていないかチェック
        if '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(
                status_code=400,
                detail="無効なファイル名です"
            )
        
        # .jsonで終わらない場合は追加
        if not filename.endswith('.json'):
            filename += '.json'
        
        # ファイルパスを構築
        file_path = os.path.join(DATA_DIR, filename)
        
        # ファイルの存在確認
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"指定されたファイル '{filename}' が見つかりません"
            )
        
        # ファイルが実際にDATA_DIR内にあることを確認（セキュリティ対策）
        real_file_path = os.path.realpath(file_path)
        real_data_dir = os.path.realpath(DATA_DIR)
        if not real_file_path.startswith(real_data_dir):
            raise HTTPException(
                status_code=400,
                detail="無効なファイルパスです"
            )
        
        # JSONファイルを読み込み
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for file {filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"ファイルの読み込み中にエラーが発生しました: JSONデータが不正です"
            )
        
        # データ構造の検証
        if 'metadata' not in data or 'pages' not in data:
            raise HTTPException(
                status_code=500,
                detail="ファイルのデータ形式が不正です"
            )
        
        # PydanticモデルでバリデーションしながらStorybookDataに変換
        try:
            storybook_data = StorybookData(**data)
        except Exception as e:
            logger.error(f"Data validation error for file {filename}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"データのバリデーション中にエラーが発生しました: {str(e)}"
            )
        
        logger.info(f"Successfully retrieved storybook: {filename}")
        return storybook_data
        
    except HTTPException:
        # HTTPExceptionはそのまま再発生させる
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting storybook {filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"絵本データの取得中に予期しないエラーが発生しました: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9998)
