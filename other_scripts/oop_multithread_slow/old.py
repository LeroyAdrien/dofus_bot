def click_next_target(self):
    # Select where the next click will occur

    # Prioritize :
    # "OK" Button / Crosses
    # "Faucher" Button
    # resource image

    mouse = Controller()

    targets = self.targets
    target_i = 0

    for target_label in ["faucher", "wheat"]:
        if len(targets[target_label]) > 0:
            target_pos = targets[target_label][0]
            print('Moving mouse to x:{} y:{}'.format(target_pos[0], target_pos[1]))
            # move the mouse
            gui.moveTo(x=target_pos[0] / 2, y=target_pos[1] / 2)
            # short pause to let the mouse movement complete
            sleep(np.random.uniform(0.197, 0.252))
            mouse.click(Button.left)

        sleep(np.random.uniform(0.2, 0.35))

        # We retake a screenshot
        self.screenshot = gui.screenshot()
        self.screenshot = np.array(self.screenshot)
        self.screenshot = cv.cvtColor(self.screenshot, cv.COLOR_RGB2BGR)

        # We search for a confirmation button
        action_button, best = self.find_rectangles_template_match(self.action_img, threshold=0.7, return_scores=True)
        self.validation_button = self.find_targets(action_button)

        if len(self.validation_button) > 0:
            self.bot_state = BotState.GATHERING
            self.time_since_last_action = time()
            coord = self.validation_button[0]

            x = coord[0] / 2
            y = coord[1] / 2

            print('Click on confirmed target at x:{} y:{}'.format(x, y))
            gui.moveTo(x=x, y=y)
            sleep(np.random.uniform(0.350, 0.668))
            mouse.click(Button.left)

            # save this position to the click history
            self.click_history.append(target_pos)
            self.validation_button = []
            found_resource = True

            return True
