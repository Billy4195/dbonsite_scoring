#!/bin/bash
docker run --link onsite:mysql -v `pwd`:/home/test -w /home/test --rm mysql:5.7 sh -c "exec mysql -h\"\$MYSQL_PORT_3306_TCP_ADDR\" -P\"\$MYSQL_PORT_3306_TCP_PORT\" -uroot -p\"passwd\" exam -N < $1 > $3"
cat $3 | sed 's/\t/,/g' > $2
rm -f $3
