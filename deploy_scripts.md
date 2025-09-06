# Скрипты для деплоя бота

## git_push.sh
Скрипт для отправки изменений в git (без токенов)

## auto_update.sh  
Скрипт для автоматического обновления бота на сервере

## update_server.sh
Скрипт для обновления сервера через SSH

## Использование

1. Для отправки в git используйте:
```bash
git add .
git commit -m "Your message"
git push origin main
```

2. Для обновления на сервере:
```bash
ssh root@92.63.100.172
cd ~/Nu_sho_ti_golova_bot
git pull origin main
docker restart nu_sho_ti_golova_bot
```
