uwsgi --plugin python34\
      --virtualenv /home/micha/projects/mediate/source/repos/book_items_env/\
      --socket 127.0.0.1:1977\
      --chdir /home/micha/projects/mediate/source/repos/book_items\
      --wsgi-file /home/micha/projects/mediate/source/repos/book_items/wsgi.py\
      --logto /home/micha/projects/mediate/source/repos/book_items/logs/uwsgi.log --log-date --log-5xx --master\
      --processes 4\
      --threads 4\
      --need-app\
      --static-map /static=/home/micha/projects/mediate/source/repos/book_items/static

