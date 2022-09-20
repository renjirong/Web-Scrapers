import numpy as np

sourceList = [  "bn_malwaretips",		
                "bn_computips",		
                "bn_pcrisk",			
                "bn_adwareguru",		
                "bn_myantispyware",	
                "bn_cyclonis",			
                "bn_howtofixguide",	
                "bn_regrunreanimator",	
                "bn_malwareguide",		
                "bn_howtomalware",		
                "bn_2spyware",
                "bn_greatis",			
                "bn_trojankiller",		
                "bn_pcriskyoutube",	
                "bn_virusremovalinfo",	
                "bn_cleanupallthreats"]




def main():
    with open("linkList.txt", "r") as f:
        data = f.read()   
    data = data.strip().split("\n")
    
    for i in range(len(data)):
        data[i] = data[i].strip()
    
    keys, counts = np.unique(data, return_counts=True)

    dict = {}

    for i in range(len(keys)):
        dict.update({keys[i] : counts[i]})
    
        
    for i in sourceList:
        try:
            print(f"{i} \t\t- {int(dict[i]/2)} \tLink(s) Collected")
        except:
            print(f"{i} \t\t- No Update")
        
        
if __name__ == "__main__":
    main()