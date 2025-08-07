#version 460

layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;



//constants
const vec2 V2_ONE_nONE = vec2(1, -1);
const vec2 V2_ZERO_ONE = vec2(0, 1);
const vec4 point_color = vec4(0.0, 0.0, 0.0, 1.0);
const vec4 line_color = vec4(0.522, 0.522, 0.522, 1.0);
const vec4 red = vec4(1.0, 0.0, 0.0, 1.0);
const vec4 green = vec4(0.0, 1.0, 0.0, 1.0);
//

//data viewport and its derived vars
uniform vec2 data_viewport_start;
uniform vec2 data_viewport;
uniform vec2 margin_percentages;
vec2 margin = data_viewport * margin_percentages;
vec2 twox_margin = margin*2;
//

//camera viewport and its derived vars
uniform vec2 camera_viewport_start;
uniform vec2 camera_viewport;
vec2 camera_viewport_inverse = 1.0/camera_viewport;
//

//other uniforms
uniform int rooted_total; //for work group splitting
uniform int data_split; //for line trace splitting
uniform ivec2 mouse_pos; //for data_point highlighting and return
//


//image stuff
layout(binding = 1, rgba8) uniform image2D image;
ivec2 image_size = imageSize(image);
//

//data points
layout(std430, binding = 4) buffer ssbo
{
    vec2 data[];
};
int data_len = data.length();
//










void surrounding_store(ivec2 pixel_pos, vec4 color)
{

    // Center of the circle
    imageStore(image, pixel_pos + ivec2(0, 0), color);

    // Radius 1
    imageStore(image, pixel_pos + ivec2(1, 0), color);
    imageStore(image, pixel_pos + ivec2(-1, 0), color);
    imageStore(image, pixel_pos + ivec2(0, 1), color);
    imageStore(image, pixel_pos + ivec2(0, -1), color);

    // Radius 2
    imageStore(image, pixel_pos + ivec2(2, 0), color);
    imageStore(image, pixel_pos + ivec2(-2, 0), color);
    imageStore(image, pixel_pos + ivec2(0, 2), color);
    imageStore(image, pixel_pos + ivec2(0, -2), color);
    imageStore(image, pixel_pos + ivec2(1, 1), color);
    imageStore(image, pixel_pos + ivec2(-1, 1), color);
    imageStore(image, pixel_pos + ivec2(1, -1), color);
    imageStore(image, pixel_pos + ivec2(-1, -1), color);

    // Radius 3
    imageStore(image, pixel_pos + ivec2(3, 0), color);
    imageStore(image, pixel_pos + ivec2(-3, 0), color);
    imageStore(image, pixel_pos + ivec2(0, 3), color);
    imageStore(image, pixel_pos + ivec2(0, -3), color);
    imageStore(image, pixel_pos + ivec2(2, 1), color);
    imageStore(image, pixel_pos + ivec2(2, -1), color);
    imageStore(image, pixel_pos + ivec2(-2, 1), color);
    imageStore(image, pixel_pos + ivec2(-2, -1), color);
    imageStore(image, pixel_pos + ivec2(1, 2), color);
    imageStore(image, pixel_pos + ivec2(-1, 2), color);
    imageStore(image, pixel_pos + ivec2(1, -2), color);
    imageStore(image, pixel_pos + ivec2(-1, -2), color);

    // Radius 4
    imageStore(image, pixel_pos + ivec2(4, 0), color);
    imageStore(image, pixel_pos + ivec2(-4, 0), color);
    imageStore(image, pixel_pos + ivec2(0, 4), color);
    imageStore(image, pixel_pos + ivec2(0, -4), color);
    imageStore(image, pixel_pos + ivec2(3, 1), color);
    imageStore(image, pixel_pos + ivec2(3, -1), color);
    imageStore(image, pixel_pos + ivec2(-3, 1), color);
    imageStore(image, pixel_pos + ivec2(-3, -1), color);
    imageStore(image, pixel_pos + ivec2(1, 3), color);
    imageStore(image, pixel_pos + ivec2(-1, 3), color);
    imageStore(image, pixel_pos + ivec2(1, -3), color);
    imageStore(image, pixel_pos + ivec2(-1, -3), color);
    imageStore(image, pixel_pos + ivec2(2, 2), color);
    imageStore(image, pixel_pos + ivec2(2, -2), color);
    imageStore(image, pixel_pos + ivec2(-2, 2), color);
    imageStore(image, pixel_pos + ivec2(-2, -2), color);

}


void draw_line(vec2 norm_pos_1, vec2 norm_pos_2, ivec2 im_size)
{
    vec2 difference = (norm_pos_2-norm_pos_1) * im_size;

    ivec2 pixeled_pos_1 = ivec2(im_size * norm_pos_1);
    ivec2 pixeled_pos_2 = ivec2(im_size * norm_pos_2);

    ivec2 pixeled_difference = min(abs(pixeled_pos_2-pixeled_pos_1), im_size); //if you zoom in really far, the raw pixel distance will get very large and be slowed down in the for loop below
    

    float slope = difference.y/difference.x;
    float inverse_slope = 1.0/slope;

    for (int i=0; i < pixeled_difference.x; i++)
    {
        imageStore(image, ivec2((i*sign(difference.x))+pixeled_pos_1.x, int((i*sign(difference.x))*slope)+pixeled_pos_1.y), line_color);
    }

    for (int i=0; i < pixeled_difference.y; i++)
    {
        imageStore(image, ivec2(int((i*sign(difference.y))*inverse_slope)+pixeled_pos_1.x, (i*sign(difference.y))+pixeled_pos_1.y), line_color);
    }
}


void main()
{
    uint split_invocation = (rooted_total * (gl_GlobalInvocationID.y)) + gl_GlobalInvocationID.x;
    //split_invocation = gl_GlobalInvocationID.x;
    vec2 data_point = data[split_invocation]; //the actual data point
    bool data_point_is_nan = isnan(data_point.y);
    if (data_point[0] == 0)
    {
        // do nothing
        /*
        For some weird reason, on intel igpus, 
        we need this if statement to prevent the first data point 
        from being drawn in the wrong spot. 
        I have no idea why this happens.
        I think it is insane too.
        */
    }
    //NULL CULLING
    if (data_point_is_nan)
    {
        return;
    }
    

    //vec2 data_point_location_normalized = (V2_ONE_nONE*(data_point-data_viewport_start + margin)/(data_viewport + twox_margin)+V2_ZERO_ONE - camera_viewport_start)*camera_viewport_inverse; //between 0.0 and 1.0 for positioning

    vec2 data_point_location_normalized = (V2_ONE_nONE*(data_point-data_viewport_start + margin)/(data_viewport + twox_margin)+V2_ZERO_ONE - camera_viewport_start)*camera_viewport_inverse; //between 0.0 and 1.0 for positioning
    vec2 data_point_position_pixelized = data_point_location_normalized * image_size;
    ivec2 data_point_position_pixelized_fixed = ivec2(data_point_position_pixelized);

    vec2 last_data_point = data[split_invocation-1]; //the actual data point
    vec2 last_data_point_location_normalized = (V2_ONE_nONE*(last_data_point-data_viewport_start + margin)/(data_viewport + twox_margin)+V2_ZERO_ONE - camera_viewport_start)*camera_viewport_inverse; //between 0.0 and 1.0 for positioning
    vec2 last_data_point_position_pixelized = last_data_point_location_normalized * image_size;
    ivec2 last_data_point_position_pixelized_fixed = ivec2(last_data_point_position_pixelized);

    //offscreen culling
    bool current_dp_offscreen = (data_point_position_pixelized_fixed.x > image_size.x || data_point_position_pixelized_fixed.y > image_size.y || data_point_position_pixelized_fixed.x < 0 || data_point_position_pixelized_fixed.y < 0);
    bool last_dp_offscreen = (last_data_point_position_pixelized_fixed.x > image_size.x || last_data_point_position_pixelized_fixed.y > image_size.y || last_data_point_position_pixelized_fixed.x < 0 || last_data_point_position_pixelized_fixed.y < 0);
    if (last_dp_offscreen && current_dp_offscreen)
    {
        return;
    }


    
    int cross_line_preventer = int(mod(split_invocation, data_split) != 0);
    draw_line(last_data_point_location_normalized, data_point_location_normalized, image_size * int(!isnan(data_point.y)) * cross_line_preventer);


    if (distance(data_point_position_pixelized_fixed, mouse_pos) < 20)
    {
        data[data_len-1] = data_point;
        data[data_len-2] = data_point_position_pixelized;
    }
    //color_for_point.g = (20.0/distance(data_point_position_pixelized_fixed, mouse_pos));
    surrounding_store(data_point_position_pixelized_fixed, point_color);
}