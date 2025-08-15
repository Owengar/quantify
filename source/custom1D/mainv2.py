import pygame, moderngl, struct, numpy, time, math, json, sys, os, threading
import display_manager_, input_, surface_, viewport_, program_manager_, labeling_, data_ingester_, error_corrector_


#imports for debugging
import cProfile, subprocess


print("main running!")

window_size = (1600, 1400)
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





	display_manager = display_manager_.display_manager(window_size, "1D Plotter", (14, 40, 66, 255), scaled_up=False)
	display_manager.ctx.disable(moderngl.DEPTH_TEST)
	program_manager = program_manager_.program_manager(".\\programs\\programs2.json", display_manager)
	input = input_.input(".\\care_keys.json")
	label_surface = surface_.surface(window_size, display_manager, flags=pygame.SRCALPHA)
	label_surface.fill(bg_color_transparant)
	data_ingester = data_ingester_.data_ingester(running, paused, 0.1)
	data_ingester.wait_for_initial_data()
	viewport = viewport_.viewport(display_manager, program_manager.programs, data_ingester)
	labeling = labeling_.labeling(display_manager, label_surface, viewport, data_ingester)
	clock = pygame.Clock()


	draw_surface = surface_.surface(window_size, display_manager, flags=pygame.SRCALPHA)

	draw_surface.fill(bg_color)

	ssbo = display_manager.ctx.buffer(dset_1.tobytes(), dynamic=False)
	ssbo.bind_to_storage_buffer(4)
	error_corrector = error_corrector_.error_corrector(1, ssbo, data_ingester)
	error_corrector.start_correction()
	draw_surface.bind_to_image(1)
	program_manager.programs["label"]["label_texture"] = 3


	data_ingester.ingest()
	formatted_dset = data_ingester.format_data(0, 0)
	deletion_indices = []
	chosen_indices = []
	for i in range(len(formatted_dset)):
		if i%50 != 0:
			deletion_indices.append(i)
		else:
			chosen_indices.append(i)


	data_ingester.start_ingest_thread()
	data_wrote_accumulation = 0
	start_index = 0
	end_index = 0
	while running[0]:

		#Run input loop
		input.input_loop(running)
		viewport.mouse_drag(input)
		viewport.zoom(input)



		if input.keys_down[pygame.K_SPACE]:
			paused[0] = not paused[0]
		if input.keys_down[pygame.K_ESCAPE]:
			viewport.set_camera_viewport_start((0, 0))
			viewport.set_camera_viewport((1, 1))

		formatted_dset = data_ingester.latest_formatted_dset #data_ingester.format_data(0, 0)
		total = len(formatted_dset)
		rooted_total = math.ceil(total ** 0.5)
		program_manager.programs["new_compute"]["rooted_total"] = rooted_total
		program_manager.programs["new_compute"]["data_split"] = data_ingester.data_trace_splits[0]
		program_manager.programs["new_compute"]["mouse_pos"] = input.mouse_pos

		end_index = data_ingester.setp_index
		if input.keys_down[pygame.K_SPACE] and False: 
			print(formatted_dset)
			print("\n\n")
			print(f"{start_index}, {end_index}")
			print(f"byte offset : {(start_index*4*2)}")
			print("\n~")
		if start_index != end_index:
			data_wrote_accumulation += len(formatted_dset[start_index:end_index])
			print(f"wrote {len(formatted_dset[start_index:end_index])} points to SSBO, {data_wrote_accumulation}/{len(formatted_dset)}")
			ssbo.write(formatted_dset[start_index:end_index], offset=(start_index*4*2))
			start_index = end_index

		###precalcs
		viewport.pre_calc_viewports()
		###
		display_manager.run_compute(program_manager.programs["new_compute"], (rooted_total, rooted_total, 1))
		error_corrector.check_for_request(formatted_dset)










		#draw labels and axes
		labeling.draw_axis_lines(label_surface.pyg_surf, bg_color)
		labeling.make_grid_list()
		labeling.draw_hovering(ssbo, input.mouse_pos)
		

		fps_text = labeling.fps_font.render(f"fps: {clock.get_fps()}", False, (0, 0, 0, 255))
		label_surface.blit(fps_text, (0, 0))
		pygame.draw.circle(label_surface.pyg_surf, (0, 255, 0, 255), (labeling.margin_size, (window_size[1]-labeling.margin_size)), 3)
		pygame.draw.circle(label_surface.pyg_surf, (0, 255, 0, 255),  (window_size[0], 0), 3)
		



		#overall screen render
		display_manager.render(program_manager.programs["label"], [(label_surface.write_and_return(), 3)])


		pygame.display.flip()
		label_surface.fill(bg_color_transparant)
		draw_surface.write_to_texture()
		clock.tick()

	


if __name__ == "__main__":
	#cProfile.run('main()', filename="stat.txt", sort=2)
	main()
	print("out")
	pygame.quit() #if we don't call this then it might freeze
	print("pygame quited")
	os.abort() # we need to abort or else the shutdown takes forever!