       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCOUNT-VERIFY.

       DATA DIVISION.
       WORKING-STORAGE SECTION.

       * Input values
       01 WS-INPUT.
          05 WS-ACCOUNT-NO     PIC X(10).
          05 WS-PIN            PIC X(4).

       * Simulated account record
       01 WS-ACCOUNT-RECORD.
          05 WS-STORED-ACCOUNT PIC X(10) VALUE "1234567890".
          05 WS-STORED-PIN     PIC X(4)  VALUE "4321".
          05 WS-STATUS         PIC X(10) VALUE "ACTIVE".

       01 WS-RESULT PIC X(30).

       PROCEDURE DIVISION.

       MAIN-PARA.

           DISPLAY "ENTER ACCOUNT NUMBER: ".
           ACCEPT WS-ACCOUNT-NO.

           DISPLAY "ENTER PIN: ".
           ACCEPT WS-PIN.

           PERFORM VERIFY-ACCOUNT.

           DISPLAY WS-RESULT.

           STOP RUN.

       VERIFY-ACCOUNT.

           IF WS-ACCOUNT-NO NOT = WS-STORED-ACCOUNT
               MOVE "ACCOUNT NOT FOUND" TO WS-RESULT

           ELSE
               IF WS-STATUS NOT = "ACTIVE"
                   MOVE "ACCOUNT NOT ACTIVE" TO WS-RESULT

               ELSE
                   IF WS-PIN = WS-STORED-PIN
                       MOVE "ACCOUNT VERIFIED" TO WS-RESULT
                   ELSE
                       MOVE "INVALID PIN" TO WS-RESULT
                   END-IF
               END-IF
           END-IF.