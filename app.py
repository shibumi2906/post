import os
from fastapi import FastAPI, HTTPException, Query
import openai

# Инициализация FastAPI-приложения
app = FastAPI(title="Генератор блог-постов с OpenAI")

# Укажите свой API-ключ OpenAI
openai.api_key = "ВАШ_API_КЛЮЧ"

# ============================================================================
# Функции генерации контента
# ============================================================================

def generate_post(topic: str) -> str:
    """
    Генерирует краткий пост для блога на заданную тему.
    """
    prompt_post = f"Напишите подробный пост для блога на тему: {topic}."
    response_post = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Если эта модель недоступна, замените на актуальную, например, "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt_post}],
        max_tokens=50,
        temperature=0.7,
    )
    post_content = response_post.choices[0].message.content.strip()
    return post_content

def generate_extended_post(topic: str) -> dict:
    """
    Генерирует расширенный контент для блога, который включает:
    - привлекательный заголовок,
    - мета-описание,
    - подробный пост с SEO-оптимизацией.
    """
    # Генерация заголовка
    prompt_title = f"Придумайте привлекательный заголовок для поста на тему: {topic}"
    response_title = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_title}],
        max_tokens=50,
        temperature=0.7,
    )
    title = response_title.choices[0].message.content.strip()

    # Генерация мета-описания
    prompt_meta = f"Напишите краткое, но информативное мета-описание для поста с заголовком: {title}"
    response_meta = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_meta}],
        max_tokens=100,
        temperature=0.7,
    )
    meta_description = response_meta.choices[0].message.content.strip()

    # Генерация содержимого поста
    prompt_post = (
        f"Напишите подробный и увлекательный пост для блога на тему: {topic}. "
        "Используйте короткие абзацы, подзаголовки, примеры и ключевые слова для лучшего восприятия и SEO-оптимизации."
    )
    response_post = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_post}],
        max_tokens=2048,
        temperature=0.7,
    )
    post_content = response_post.choices[0].message.content.strip()

    return {
        "title": title,
        "meta_description": meta_description,
        "post_content": post_content
    }

# ============================================================================
# FastAPI-эндпоинты
# ============================================================================

@app.get("/generate", summary="Генерация поста по заданной теме")
async def generate(topic: str = Query(..., description="Тема для генерации поста"),
                   mode: str = Query("extended", description="Режим генерации: 'basic' или 'extended'")):
    """
    GET-эндпоинт для генерации поста.
    
    **Параметры:**
    - **topic**: тема для генерации поста;
    - **mode**: режим генерации. При значении 'basic' возвращается краткий пост,
      при значении 'extended' — расширенный вариант с заголовком и мета-описанием.
    
    **Пример запроса:**
    ```
    GET /generate?topic=Дизайн+интерьеров&mode=extended
    ```
    """
    try:
        if mode.lower() == "basic":
            content = generate_post(topic)
            return {"post": content}
        elif mode.lower() == "extended":
            result = generate_extended_post(topic)
            return result
        else:
            raise HTTPException(status_code=400, detail="Неверное значение параметра mode. Используйте 'basic' или 'extended'.")
    except Exception as e:
        # В случае ошибки возвращаем сообщение с описанием
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Запуск приложения (для локального тестирования)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
