package com.boostcraft.client;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.command.v2.ClientCommandRegistrationCallback;
import net.minecraft.client.MinecraftClient;
import net.minecraft.text.Text;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import net.fabricmc.fabric.api.client.command.v2.ClientCommandSource;

import java.lang.reflect.Method;

public class ClientInit implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        ClientCommandRegistrationCallback.EVENT.register((dispatcher, registryAccess) -> {
            dispatcher.register(LiteralArgumentBuilder.<ClientCommandSource>literal("boost")
                .executes((CommandContext<ClientCommandSource> ctx) -> {
                    MinecraftClient mc = MinecraftClient.getInstance();
                    if (mc == null || mc.player == null) return 0;

                    // Attempt to read FPS from Window using reflection to remain compatible
                    int fps = -1;
                    try {
                        Object window = mc.getWindow();
                        if (window != null) {
                            try {
                                Method m = window.getClass().getMethod("getFramerate");
                                Object v = m.invoke(window);
                                if (v instanceof Integer) fps = (Integer) v;
                            } catch (NoSuchMethodException e) {
                                // try alternative name
                                try {
                                    Method m = window.getClass().getMethod("getFrameRate");
                                    Object v = m.invoke(window);
                                    if (v instanceof Integer) fps = (Integer) v;
                                } catch (NoSuchMethodException ex) {
                                    // method not found; leave fps = -1
                                }
                            }
                        }
                    } catch (Throwable t) {
                        // reflection failed, ignore and continue
                    }

                    // JVM memory info (client-side)
                    Runtime rt = Runtime.getRuntime();
                    long total = rt.totalMemory() / 1024 / 1024;
                    long free = rt.freeMemory() / 1024 / 1024;
                    long max = rt.maxMemory() / 1024 / 1024;

                    String memMsg = String.format("[BoostCraft] Client JVM Memory - Used: %d MB, Free: %d MB, Max: %d MB",
                            (total - free), free, max);

                    if (fps >= 0) {
                        mc.player.sendMessage(Text.literal(String.format("[BoostCraft] FPS: %d | %s", fps, memMsg)), false);
                    } else {
                        mc.player.sendMessage(Text.literal(String.format("[BoostCraft] FPS: (unavailable) | %s", memMsg)), false);
                    }

                    return 1;
                })
            );
        });
    }
}
