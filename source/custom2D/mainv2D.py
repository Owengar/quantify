import pygame, moderngl, struct, numpy, time, math, json, sys, os, matplotlib
import display_manager_, input_, surface_, viewport_, program_manager_, labeling_, data_ingester_, error_corrector_


#imports for debugging
import cProfile, subprocess


print("main running!")

window_size = (1000, 800)
pygame.init()
bg_color = (240, 240, 240, 255)
bg_color_transparant = (240, 240, 240, 0)

def stopwatch_function(function, *args, **kwargs):
	start = time.time()
	result = function(*args, **kwargs)
	end = time.time()
	print(f"time passed: {end-start}")
	return result






def main():

	paused = [False]
	running = [True]

	i = -1
	dset_1 = numpy.array([numpy.array([0.0, numpy.nan], dtype=numpy.float32)]*4000000) #*4000000





	display_manager = display_manager_.display_manager(window_size, "2D Plotter", bg_color, scaled_up=False)
	display_manager.ctx.enable(moderngl.DEPTH_TEST)
	display_manager.ctx.enable(moderngl.BLEND)
	program_manager = program_manager_.program_manager(".\\programs\\programs2.json", display_manager)
	inputs = input_.input(".\\care_keys.json")
	label_surface = surface_.surface(window_size, display_manager, flags=pygame.SRCALPHA)
	label_surface.fill(bg_color_transparant)
	data_ingester = data_ingester_.data_ingester(running, paused, 0.1)
	data_ingester.wait_for_initial_data()
	viewport = viewport_.viewport(display_manager, program_manager.programs, data_ingester)
	draw_surface = surface_.surface(tuple(data_ingester.setpoints_lengths), display_manager, flags=pygame.SRCALPHA)
	labeling = labeling_.labeling(display_manager, label_surface, viewport, data_ingester, draw_surface)
	target_scale = (window_size[0]-labeling.margin_size*2, window_size[1]-labeling.margin_size*2)
	draw_surface.target_scale = target_scale
	draw_surface.fill(bg_color_transparant)
	clock = pygame.Clock()

	program_manager.programs["blank"]["label_texture"] = 3
	program_manager.programs["twod"]["draw_texture"] = 2



	
	



	data_ingester.start_ingest_thread(draw_surface, matplotlib.cm.viridis)
	while running[0]:

		#Run input loop
		inputs.input_loop(running)
		viewport.mouse_drag(inputs)
		viewport.zoom(inputs)



		if inputs.keys_down[pygame.K_SPACE]:
			paused[0] = not paused[0]
		if inputs.keys_down[pygame.K_ESCAPE]:
			viewport.set_camera_viewport_start((0, 0))
			viewport.set_camera_viewport((1, 1))



		###lock action

		###



		viewport.pre_calc_viewports()
		#
		if False:
			data_range = abs(data_ingester.find_max_y()-data_ingester.find_min_y())
			def normalize_y(value):

				""" print("start")
				print(f"value = {value}")
				print(f"min = {data_ingester.find_min_y()}")
				print(f"max = {data_ingester.find_max_y()}")
				print("stop") """

				if 0 == (data_ingester.find_max_y()-data_ingester.find_min_y()):
					return 0
				return (value-data_ingester.find_min_y()) / (data_ingester.find_max_y()-data_ingester.find_min_y())
				#return abs(data_ingester.find_max_y()-value) / abs(value-data_ingester.find_min_y())

			for x in range(setpoints_lengths[0]):
				for y in range(setpoints_lengths[1]):
					
					ycol = normalize_y(formatted_dset[(y*setpoints_lengths[0]) + x]) * 255
					try:
						draw_surface.pyg_surf.set_at((x, y), (0, 0, ycol, 255))
					except:
						pass

		





		#draw labels and axes
		labeling.draw_axis_lines(label_surface.pyg_surf, bg_color)
		labeling.make_grid_list()
		labeling.update_colorbar()

		labeling.draw_hovering(inputs.mouse_pos)
		

		fps_text = labeling.fps_font.render(f"fps: {clock.get_fps()}", False, (0, 0, 0, 255))
		label_surface.blit(fps_text, (0, 0))




		#overall screen render
		display_manager.ctx_clear()
		display_manager.render(program_manager.programs["twod"], [(draw_surface.write_and_return(), 2)])
		display_manager.render(program_manager.programs["blank"], [(label_surface.write_and_return(), 3)])


		pygame.display.flip()
		label_surface.fill(bg_color_transparant)
		clock.tick()

	


if __name__ == "__main__":
	#cProfile.run('main()', filename="stat.txt", sort=2)
	main()
	print("out")
	pygame.quit() #if we don't call this then it might freeze
	print("pygame quited")
	os.abort() # we need to abort or else the shutdown takes forever!