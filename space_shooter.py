import pygame
import random
import math

# 初始化pygame
pygame.init()

# 设置游戏窗口
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("太空射击者")

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)


# 玩家飞船类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 创建飞船表面
        self.image = pygame.Surface([30, 30])
        self.image.fill(GREEN)
        # 绘制一个三角形飞船
        pygame.draw.polygon(self.image, BLUE, [(15, 0), (0, 30), (30, 30)])
        # 获取飞船的矩形区域（用于碰撞检测和定位）
        self.rect = self.image.get_rect()
        # 设置飞船初始位置（屏幕底部中央）
        self.rect.x = screen_width // 2
        self.rect.y = screen_height - 50
        # 设置飞船移动速度
        self.speed = 5
        # 射击冷却时间（防止连续快速射击）
        self.cooldown = 0

    def update(self):
        # 移动控制 - 检测键盘按键
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x > 0:  # 左移且不超出左边界
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.x < screen_width - self.rect.width:  # 右移且不超出右边界
            self.rect.x += self.speed

        # 射击冷却 - 每帧减少冷却时间
        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self):
        # 如果冷却时间为0，可以射击
        if self.cooldown == 0:
            self.cooldown = 15  # 设置冷却时间
            # 创建子弹并从飞船顶部中央发射
            return Bullet(self.rect.centerx, self.rect.top)
        return None


# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 创建子弹表面
        self.image = pygame.Surface([4, 10])
        self.image.fill(RED)
        # 获取子弹的矩形区域
        self.rect = self.image.get_rect()
        # 设置子弹初始位置（从飞船顶部中央发射）
        self.rect.x = x - 2  # 微调使子弹居中
        self.rect.y = y
        # 设置子弹速度（向上移动）
        self.speed = 7

    def update(self):
        # 每帧向上移动子弹
        self.rect.y -= self.speed
        # 如果子弹飞出屏幕顶部，删除它以释放内存
        if self.rect.y < 0:
            self.kill()


# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 创建敌人表面
        self.image = pygame.Surface([25, 25])
        self.image.fill(RED)
        # 绘制一个圆形敌人
        pygame.draw.circle(self.image, WHITE, (12, 12), 12)
        # 获取敌人的矩形区域
        self.rect = self.image.get_rect()
        # 设置敌人初始位置（随机出现在屏幕上方之外）
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        # 设置敌人下落速度（随机）
        self.speed = random.randint(1, 3)

    def update(self):
        # 每帧向下移动敌人
        self.rect.y += self.speed
        # 如果敌人飞出屏幕底部，重置位置到屏幕上方
        if self.rect.y > screen_height:
            self.rect.x = random.randint(0, screen_width - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speed = random.randint(1, 3)


# 创建精灵组 - 用于管理所有游戏对象
all_sprites = pygame.sprite.Group()  # 包含所有精灵
bullets = pygame.sprite.Group()      # 只包含子弹
enemies = pygame.sprite.Group()      # 只包含敌人

# 创建玩家
player = Player()
all_sprites.add(player)

# 创建敌人
for i in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# 游戏变量
score = 0  # 玩家得分
font = pygame.font.SysFont(None, 36)  # 创建字体对象用于显示分数
clock = pygame.time.Clock()  # 创建时钟对象用于控制帧率
running = True  # 游戏循环控制变量

# 游戏主循环
while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 如果点击关闭窗口
            running = False
        elif event.type == pygame.KEYDOWN:  # 如果按下键盘键
            if event.key == pygame.K_SPACE:  # 如果按下空格键
                bullet = player.shoot()  # 尝试射击
                if bullet:  # 如果成功创建了子弹
                    all_sprites.add(bullet)  # 添加到所有精灵组
                    bullets.add(bullet)      # 添加到子弹组

    # 更新所有精灵
    all_sprites.update()

    # 检测子弹和敌人的碰撞
    hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
    for hit in hits:
        score += 10  # 每击中一个敌人加10分
        # 创建新敌人替代被击中的敌人
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

    # 检测玩家和敌人的碰撞
    hits = pygame.sprite.spritecollide(player, enemies, False)
    if hits:  # 如果发生碰撞
        running = False  # 结束游戏

    # 绘制
    screen.fill(BLACK)  # 清空屏幕（填充黑色）

    # 绘制星空背景 - 随机绘制100个白点
    for i in range(100):
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        pygame.draw.circle(screen, WHITE, (x, y), 1)

    all_sprites.draw(screen)  # 绘制所有精灵

    # 显示分数
    score_text = font.render(f"分数: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))  # 在左上角显示分数

    pygame.display.flip()  # 更新整个显示表面
    clock.tick(60)  # 控制帧率为60FPS

# 游戏结束显示
game_over_text = font.render(f"游戏结束! 最终分数: {score}", True, WHITE)
screen.blit(game_over_text, (screen_width // 2 - 150, screen_height // 2))
pygame.display.flip()

# 等待几秒后退出
pygame.time.wait(3000)  # 等待3秒
pygame.quit()  # 退出pygame