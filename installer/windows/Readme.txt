After installation Magic Packet Server are working. You don't need to start it manually.

The Magic Packet Server consists of two services: Magic Packet Worker (mpworker) and Magic Packet Server (mpserver)

If you want to stop Magic Packet Server you shoud run following commands in the specified order:
    cd <Magic-Packet-Server-Installation-Folder>
    mpserver.exe stop
    mpworker.exe stop

Services mpworker and mpserver will start automaticaly after reboot

If you want to start Magic Packet Server manually you shoud run following commands in the specified order:
    cd <Magic-Packet-Server-Installation-Folder>
    mpworker.exe start
    mpserver.exe start

To uninstall the Magic Packet Server correctly use Control Panel -> Programs -> Programs and Features
or <Magic-Packet-Server-Installation-Folder>/uninstall/unins000.exe