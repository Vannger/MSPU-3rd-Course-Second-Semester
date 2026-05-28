import requests

BASE_URL = "http://127.0.0.1:8000"

def test_run_all_security_cases():
    print("\n[+] Запуск автоматизированного аудита безопасности доступа...")

    headers_alice = {"X-User": "alice"}
    response_idor = requests.get(f"{BASE_URL}/files/2", headers=headers_alice)
    
    assert response_idor.status_code == 404, f"FAIL: IDOR обнаружен! Статус {response_idor.status_code} вместо 404"
    print("[SUCCESS] Тест 1 (IDOR) пройден: Алиса получила 404 на файл Боба.")

    response_access = requests.get(f"{BASE_URL}/files/1", headers=headers_alice)
    
    assert response_access.status_code == 200, f"FAIL: Хозяин не может прочитать свой файл! Статус {response_access.status_code}"
    assert response_access.json()["filename"] == "report_alice.pdf"
    print("[SUCCESS] Тест 2 (Access) пройден: Алиса успешно прочитала свой файл.")

    headers_admin = {"X-User": "admin"}
    response_delete = requests.delete(f"{BASE_URL}/files/2", headers=headers_admin)
    
    assert response_delete.status_code == 200, f"FAIL: Админ не смог удалить файл! Статус {response_delete.status_code}"
    print("[SUCCESS] Тест 3 (Admin) пройден: Администратор успешно удалил чужой файл.")

    headers_bob = {"X-User": "bob"}
    response_check_deleted = requests.get(f"{BASE_URL}/files/2", headers=headers_bob)
    
    assert response_check_deleted.status_code == 404, "FAIL: Файл остался в базе после удаления админом!"
    print("[SUCCESS] Тест 4 (Verification) пройден: Проверено, файл действительно удален.")

if __name__ == "__main__":
    try:
        test_run_all_security_cases()
        print("\n[ИТОГ] Все тесты безопасности успешно PASSED! Проект защищен.")
    except AssertionError as e:
        print(f"\n[КРИТИЧЕСКАЯ ОШИБКА БЕЗОПАСНОСТИ] {e}")
