#version 430
precision mediump float;


layout(binding = 1, rgba8) uniform image2D data_image;
uniform sampler2D label_texture;
ivec2 image_size = imageSize(data_image);

in vec2 v_text; 
out vec3 f_color;








void main()
{


    vec3 data_texture = imageLoad(data_image, ivec2(v_text*image_size)).rgb;
    vec4 label_texture = texture(label_texture, v_text);
    f_color = data_texture;
    f_color *= 1-label_texture.a;
    f_color += label_texture.bgr * label_texture.a;
    //f_color = data_texture + label_texture.bgr;

    //del this
    //f_color = data_texture * 1000.0;
}