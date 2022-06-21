#include <iostream>
#include <SFML/Graphics.hpp>
#include <math.h>
#include <tuple>
#define PI 3.1415926535897932384626433832795

using namespace std;

const int screen_size[2] = {1080,720};
const int texture_size[2] = {16,16};
const int sprite_size[2] = {32,32};
const int map_size[2] = {16,11};

double test_var;

int Map[11][16] ={{1,1,1,1,1,1,1,2,1,2,1,1,1,1,1,1},
                  {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
                  {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
                  {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
                  {1,0,0,0,1,0,3,2,0,0,0,0,0,0,0,1},
                  {1,0,0,0,0,0,3,3,0,0,1,0,0,0,0,1},
                  {1,1,2,3,0,0,0,0,0,0,1,0,0,1,0,1},
                  {1,0,0,0,0,0,0,0,0,0,1,0,0,1,0,1},
                  {1,0,0,0,0,0,0,0,0,0,2,1,0,1,0,1},
                  {1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1},
                  {1,1,1,1,1,3,3,1,1,1,1,1,1,2,1,1}};

int Floor_Map[11][16] ={{1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1},
                        {1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1}};

double player_x = 3.0;
double player_y = 2.5;
double player_a = 0.0;

double m_angle;

const int FOV = 60;
const int y_FOV = screen_size[1]*FOV/screen_size[0];
const float RTX = 1.0f;
const double detail = screen_size[0]/FOV * RTX;
const double y_detail = screen_size[1]/y_FOV * RTX;
const double ray_width = screen_size[0]/(FOV*detail);
const double player_height = 1.0; // !!! Relative to tile size

const sf::Keyboard::Key RIGHT = sf::Keyboard::D;
const sf::Keyboard::Key LEFT = sf::Keyboard::Q;
const sf::Keyboard::Key UP = sf::Keyboard::Z;
const sf::Keyboard::Key DOWN = sf::Keyboard::S;

const int max_sprite_count = 124;

sf::VertexArray quads_buffer(sf::Quads);

// Textures
sf::Image walls_textures[10];
sf::Image sprites_textures[10];

sf::Color Colors[] = {sf::Color(0,0,0),sf::Color(255,0,0),sf::Color(0,255,0),sf::Color(0,0,255)};

sf::RenderWindow app(sf::VideoMode(screen_size[0], screen_size[1]), "WAW");

int sprite_count = 0;

class Sprite {
    private:

    public:
        double position_x;
        double position_y;
        double direction;
        int front_texture_index;
        int back_texture_index;

        void init(double pos_x, double pos_y, double dir, int front_tex_index, int back_tex_index) {
            sprite_count++;
            position_x = pos_x;
            position_y = pos_y;
            direction = dir;
            front_texture_index = front_tex_index;
            back_texture_index = back_tex_index;
        }
};

Sprite sprites[124];

double radians(double degrees) {
    return degrees*PI/180.0;
}

double degrees(double radians) {
    return radians*180/PI;
}

void load_textures() {
    walls_textures[0].loadFromFile("resources/stone_wall.png");
    walls_textures[1].loadFromFile("resources/broken_stone_wall.png");
    walls_textures[2].loadFromFile("resources/mossy_stone_wall.png");

    sprites_textures[0].loadFromFile("resources/ennemy_front.png");
    sprites_textures[1].loadFromFile("resources/ennemy_back.png");
}

sf::Color shade_color(sf::Color color, double shade) {
    return sf::Color(color.r*shade,color.g*shade,color.b*shade);
}

tuple<int,int,bool> AIE(int x,int y) {
    int new_x=max(min(x,map_size[0]-1),0);
    int new_y=max(min(y,map_size[1]-1),0);
    return {new_x,new_y,new_x!=x or new_y!=y};
}

tuple<double,int,double,char> cast_ray(double x, double y, double angle) { //Returns Distance , MapValue , Offset , HitType , Sprites_Distances , Sprites side&offset
    double V_d = 1000000 ; double H_d = 1000000;
    // Horizontal
    double H_first_x,H_first_y,H_xStep,H_yStep,H_y_modifier,H_x,H_y,x_offset,y_offset;
    int H_map_value,V_map_value;

    if(abs(sin(angle))>10e-5) {
        if(sin(angle)>0) {
            H_first_y = ceil(y) - y;
            H_y_modifier = 0.1;
            H_yStep = 1;
        } else {
            H_first_y = int(y)-y;
            H_y_modifier = -0.1;
            H_yStep = -1;
        }
        H_first_x = H_first_y/tan(angle);
        H_xStep = 1/tan(H_yStep*angle);

        for(int H_i = 0; H_i<2048; H_i++) {
            H_x = x+H_first_x + H_xStep*H_i;
            H_y = y+H_first_y + H_yStep*H_i;
            auto [H_mx,H_my,changed]=AIE(int(H_x),int(H_y+H_y_modifier));

            H_map_value = Map[H_my][H_mx];
            if(H_map_value or changed) {
                H_d = sqrt(pow(H_first_x + H_xStep*H_i, 2) + pow(H_first_y + H_yStep*H_i, 2));
                break;
            }
        }
    }
    // Vertical
    double V_first_x,V_first_y,V_xStep,V_yStep,V_x_modifier,V_x,V_y;
    if(abs(cos(angle))>10e-5) {
        if(cos(angle)>0) {
            V_first_x = ceil(x) - x;
            V_x_modifier = 0.1;
            V_xStep = 1;
        } else {
            V_first_x = int(x) - x;
            V_x_modifier = -0.1;
            V_xStep = -1;
        }
        V_first_y = V_first_x*tan(angle);
        V_yStep = tan(V_xStep*angle);

        for(int V_i = 0; V_i<2048; V_i++) {
            V_x = x+V_x_modifier + V_xStep*V_i;
            V_y = y+V_first_y + V_yStep*V_i;
            auto [V_mx,V_my,changed] = AIE(int(V_x+V_first_x),int(V_y));

            V_map_value = Map[V_my][V_mx];
            if(V_map_value or changed) {
                V_d = sqrt(pow(V_first_x + V_xStep*V_i, 2) + pow(V_first_y + V_yStep*V_i, 2));
                break;
            }
        }
    }

    double distance = min(V_d,H_d);

    //Floor
    double dtp,x_hit,y_hit; //DistanceToPlayer
    for(int a=1; a<y_FOV*y_detail; a++) {
        dtp = tan(radians(a/y_detail))*player_height;
        if(dtp >= distance) continue;
        x_hit = player_x + cos(angle)*dtp;
        y_hit = player_y + sin(angle)*dtp;

    }



    // Return
    if(distance == H_d) {
        if(sin(angle)>0) {
            x_offset = H_x - int(H_x);
        } else {
            x_offset = ceil(H_x) - H_x;
        }
        return {H_d,H_map_value,x_offset,'h'};
    } else {
        if(cos(angle)<0) {
            y_offset = V_y - int(V_y);
        } else {
            y_offset = ceil(V_y) - V_y;
        }
        return {V_d,V_map_value,y_offset,'v'};
    }

}

double AFE(double distance, double angle_modifier) { // Avoid Fisheye Effect
    return cos(angle_modifier)*distance;
}

void add_rect_to_buffer(double x, double y, double size_x, double size_y, sf::Color color) {
    quads_buffer.append(sf::Vertex(sf::Vector2f(  x,   y), color));
    quads_buffer.append(sf::Vertex(sf::Vector2f(  x + size_x, y), color));
    quads_buffer.append(sf::Vertex(sf::Vector2f(x + size_x, y + size_y), color));
    quads_buffer.append(sf::Vertex(sf::Vector2f(x, y + size_y), color));

}

void render(double ray, int ray_id, int texture_ID, double offset, double shade) {
    // Walls
    double ray_height = (300*screen_size[1]/222)/ray;
    for(int i = 0;i<texture_size[1];i++) {
        add_rect_to_buffer(ray_id*ray_width, screen_size[1]/2 - ray_height/2 + i*ray_height/texture_size[1],
                           ray_width, ray_height/texture_size[1],
                           shade_color(walls_textures[texture_ID].getPixel(int(offset*texture_size[0]),i),shade));
    }
}

void draw_map_top_view() {
    int tile_size_x = screen_size[0]/map_size[0];
    int tile_size_y = screen_size[1]/map_size[1];

    sf::RectangleShape tile(sf::Vector2f(tile_size_x-2, tile_size_y-2));

    for(int i = 0; i<map_size[0]; i++) {
        for(int j = 0; j<map_size[1]; j++) {
            tile.setFillColor(Colors[Map[j][i]]);
            tile.setPosition(int(i*screen_size[0]/map_size[0]) + 1,int(j*screen_size[1]/map_size[1]) + 1);
            app.draw(tile);
        }
    }
    //Player
    sf::CircleShape player(10);
    player.setFillColor(sf::Color(255,255,0));
    player.setPosition(tile_size_x*player_x - 10,tile_size_y*player_y - 10);

    app.draw(player);

}

void line(int x1, int y1 , int x2, int y2, sf::Color color) {
    sf::Vertex line[] =
    {
        sf::Vertex(sf::Vector2f(x1, y1),color),
        sf::Vertex(sf::Vector2f(x2, y2),color)
    };
    app.draw(line,2,sf::Lines);
}

int main()
{
    // Font stuff
    sf::Font arial;
    arial.loadFromFile("resources/Arial.ttf");
    // FPS counter init
    sf::Clock clock;
    double oldClock = 0;
    double delta = 0;
    double currentClock;

    sf::Color color;
    int nb;
    double shade;
    // Load a sprite to display
    sprites[0].init(4.5,2.5,0.0,0,1);
    sprites[1].init(5.5,2.5,PI,0,1);

    load_textures();
	// Start the game loop
	int counter = 0;
     while (app.isOpen())
    {
        // Process events
        sf::Event event;
        while (app.pollEvent(event))
        {
            // Close window : exit
            if (event.type == sf::Event::Closed)
                app.close();
        }
        // Get inputs
        if(sf::Keyboard::isKeyPressed(RIGHT)) player_a += PI/2 * delta;
        if(sf::Keyboard::isKeyPressed(LEFT)) player_a -= PI/2 * delta;
        if(sf::Keyboard::isKeyPressed(UP) & !Map[int(player_y+sin(player_a)/4)][int(player_x+cos(player_a)/4)]) {
            player_x += cos(player_a)*2*delta; player_y += sin(player_a)*2*delta;}
        if(sf::Keyboard::isKeyPressed(DOWN) & !Map[int(player_y-sin(player_a)/4)][int(player_x-cos(player_a)/4)]) {
            player_x -= cos(player_a)*2*delta; player_y -= sin(player_a)*2*delta;}
        if(player_a < 0) player_a += 2*PI;
        if(player_a > 2*PI) player_a -= 2*PI;


        // Clear screen
        app.clear();
        quads_buffer.clear();
        // Update the window

        // Rendering
        nb = 0;
        test_var = 0;
        for(double modifier = -FOV*detail/2; modifier <= FOV*detail/2; modifier++) {
            m_angle = player_a + radians(modifier/detail);
            auto [distance,map_value,offset,hit_type] = cast_ray(player_x,player_y,m_angle);
            distance = AFE(distance,radians(modifier/detail));
            /*
            line(int(player_x * screen_size[0]/map_size[0]),int(player_y * screen_size[1]/map_size[1]),
                 int((player_x+cos(m_angle)*distance) * screen_size[0]/map_size[0]),
                 int((player_y+sin(m_angle)*distance) * screen_size[1]/map_size[1]),color); */
            if(hit_type == 'h') {
                shade = 0.8;
            } else {
                shade = 1.0;
            }
            render(distance,nb,map_value - 1,offset,shade);
            nb++;
        }
        //cout << test_var << endl;
        sprites[0].direction += PI/4 * delta;
        app.draw(quads_buffer);
        app.display();


        // Fancy FPS action
        currentClock = clock.restart().asSeconds();
        delta = currentClock - oldClock;
        counter++;
        if(counter%10 == 0) {
            app.setTitle("Super jeu : FPS:"+to_string(int(1/delta)));
            counter = 0;
        }
    }

    cout << sprite_count << endl;
    return EXIT_SUCCESS;
}
