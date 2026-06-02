# Отчет по ДЗ №6

## Скриншот успешной XSS-атаки (до защиты).
<img width="1920" height="1080" alt="Снимок экрана (331)" src="https://github.com/user-attachments/assets/5d173565-129e-4054-ab32-7e9f03035379" />

## Пример кода функции-санитизера.
``` 
safe_message = clean_html(user_comment)
comments_db.append(safe_message)
```

## Скриншот заголовков ответа (вкладка Network), где виден CSP.
<img width="1920" height="1080" alt="Снимок экрана (332)" src="https://github.com/user-attachments/assets/12375c36-2274-439d-b586-caf6ee449a0f" />

## Скриншот заблокированной атаки (из консоли браузера).
<img width="1920" height="1080" alt="Снимок экрана (333)" src="https://github.com/user-attachments/assets/aa0894fa-8499-4082-bcb6-187f1adf9228" />

