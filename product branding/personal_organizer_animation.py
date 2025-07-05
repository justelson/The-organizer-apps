from manim import *

class PersonalOrganizerpresentation(Scene):
    def construct(self):
        self.camera.background_color = BLACK    # Set the background color to black

        comlogo = SVGMobject(file_name="imges media/company logo.svg")
        title = Text("Personal Organizer",font="Boldonse", font_size=72, color=WHITE).shift(RIGHT*1.5).scale(0.7)
        title.set_color_by_gradient(
            "#4B0082",  # Dark Purple
            "#800080",
            "#A64CA6",
            "#C080C0",
            "#D9A6D9",
            "#E6CCE6"   # Light Purple
        )
            

        icon = SVGMobject(file_name="imges media/app icon.svg").scale(0.5).next_to(title, LEFT, buff=0.5)
        icon.set_color(PURPLE_E)


        self.play(Write(comlogo), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(comlogo), run_time=0.5)
        self.wait(1.5)
        self.play(Write(title)
        , Create(icon), run_time=2)

        self.wait(1)
        self.play(FadeOut(title), FadeOut(icon), run_time=2)
        self.wait(0.5)



        # create app use demo 
        button = Text("Time to Organize Files", font="Boldonse", font_size=72, color=WHITE).shift(ORIGIN).scale(0.7)
        button.set_color_by_gradient(
            "#4B0082",  # Dark Purple
            "#800080",
            "#A64CA6",
            "#C080C0",
            "#D9A6D9",
            "#E6CCE6"   # Light Purple
        )
        reca=SurroundingRectangle(button, color=PURPLE, buff=0.1,corner_radius=0.1).set_fill(PURPLE, opacity=0.5)
        buttongroup = VGroup(button, reca)

        self.play(Write(buttongroup), run_time=2)


        #create mouse to click button 
        mouse = SVGMobject(file_name="imges media/mouse.svg", color=LOGO_WHITE).scale(0.5).shift(DOWN*0.8+LEFT*2)
        self.play(Write(mouse), run_time=2)
        
        self.play(mouse.animate.shift(UP*0.5), run_time=1.5)

        lastdot = Dot(radius=20, color=ORANGE).move_to(mouse.get_center())

        self.play(Indicate(buttongroup),
                  Indicate(mouse),run_time=1)


        self.play(GrowFromCenter(lastdot),FadeOut(lastdot, mouse, buttongroup), run_time=0.5)
        



        self.wait(2)