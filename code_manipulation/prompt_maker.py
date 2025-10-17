import pyperclip

class Matcher:
    def __init__(self):
        self.start_prompt = """
        You are a professional PhD art professor, knowledgeable in all of the arts in the world. You are given a task of matching images WITH their correct code.
        To do so, you will use your assistants descriptions of each image to potentially match it with the correct code ( that has the images METADATA connected to ).
        
        You will then return me THREE results in a JSON styled answer. NOTHING ELSE. JUST THESE THREE ELEMENTS.
        
        FIRST, for every SUCCESSFUL Image you think matches with their code you will put in a json object. The key is the Image's name, and value being the matched code. This object key is "matched_images: {}"
        SECOND, for every Image which you COULDN'T match with an available code you will put in a list named "images_no_code: []"
        THIRD, for every Code which you COULDN'T match with an available image you will put in a list named "codes_no_images: []"
        
        NOW, you're assistant may have made SOME MISTAKES. Some codes could've been typed incorrectly, some might be outright missing, some images might be corrupted ect... That's why you will need to return those three things. The image descriptions your assistant is giving you WILL ALWAYS be correct.
        One little thing that may help. USUALLY ( and this is usually ) images are scanned and placed next to each other. Not all the time, but this should be taken into consideration ( meaning first code should match first image, second one second, ect... ), But of course there could be the errors I mentioned before. Some images that should've been in the middle are scanned last. But even then, after those couple of images it should return to going in order. Use the descriptions to help you make an educated guess.
        
        REMEMBER, not ALL CODES HAVE to be connected to an image. so it's FINE, if an image is missing a code OR the other way around.
        BUT STILL, TRY TO GET AS MUCH AS YOU CAN, IF IT AT LEAST SEMI MAKES SENSE FOR THE CODES TO BE CONNECTED !!!!
        
        Also, each CODE can ONLY be linked to ONE image. ONE IMAGE PER ONE CODE. Do NOT reuse codes for multiple images !
        
        GOOD LUCK and THANK YOU PROFESSOR !!! \n\n
        """

        filling_code_info = ""
        with open("filling_codes.txt", "r") as file:
            filling_code_info = file.read()

        self.filling_info = """
        FIRST, I will give you some info on what the filling codes mean that is attached to each code's metadata down below: \n\n
        """ + filling_code_info + "\n\n"

        self.code_info = """ \n\n
        NEXT, Here are the codes WITH their metadata attached that need linking to the images: \n\n
        """

        self.image_list = """ \n\n
        AND finally, here are all the images in order with their extracted features that YOU need to match to the correct code: \n\n
        """

        self.final_prompt = """
        \n\n\n
        I'll REITERATE THE TASK NOW: \n\n
        """ + self.start_prompt

    def send_prompt(self, code_list, image_descriptions):
        prompt = self.start_prompt + self.filling_info + self.code_info + code_list + self.image_list + image_descriptions + self.final_prompt

        print(prompt)
        pyperclip.copy(prompt)
