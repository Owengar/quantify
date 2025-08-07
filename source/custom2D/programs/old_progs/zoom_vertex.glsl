#version 430


in vec2 vert;
in vec2 in_text;
out vec2 v_text;




uniform vec2 camera_viewport; //from 0.0 - 1.0
uniform vec2 camera_viewport_start;




void main()
{
    vec2 camera_viewport_inverse = 1.0/camera_viewport;


    gl_Position = vec4((vert-camera_viewport_start)*camera_viewport_inverse, 0.0, 1.0);
    v_text = in_text;

}