Distribute and collect complete folders recursive to/from multiple clients in LAN.

./sync.sh <mode>

Available modes are:
    
    --share-each        Shares files with the devices as they exist in their share directories.
                        WARNING: The share directories are CLEARED.
                        
    --share-all         Shares files from the common directory to the devices.
                        WARNING: The share directories are CLEARED, the common directory stays AS IS.
                        
    --fetch             Fetches all files from the devices and stores them in the corresponding directory.
