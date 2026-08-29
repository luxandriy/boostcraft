package com.boostcraft;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import com.mojang.brigadier.context.CommandContext;
import net.minecraft.server.command.ServerCommandSource;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.text.Text;

public class BoostCraft implements ModInitializer {
    @Override
    public void onInitialize() {
        // Register a server-side /boost command that shows JVM memory usage.
        CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) -> {
            dispatcher.register(LiteralArgumentBuilder.<ServerCommandSource>literal("boost")
                .executes((CommandContext<ServerCommandSource> ctx) -> {
                    ServerCommandSource source = ctx.getSource();

                    // Memory info (in MB)
                    Runtime rt = Runtime.getRuntime();
                    long total = rt.totalMemory() / 1024 / 1024;
                    long free = rt.freeMemory() / 1024 / 1024;
                    long max = rt.maxMemory() / 1024 / 1024;

                    String msg = String.format("[BoostCraft] JVM Memory - Used: %d MB, Free: %d MB, Max: %d MB",
                            (total - free), free, max);

                    if (source.getEntity() instanceof ServerPlayerEntity) {
                        source.sendFeedback(Text.literal(msg), false);
                    } else {
                        source.sendFeedback(Text.literal(msg), false);
                    }

                    // Hint about client-side FPS command
                    source.sendFeedback(Text.literal("Run the client-side /boost command to see FPS and client memory (only available in singleplayer or when run on the client)."), false);

                    return 1;
                })
            );
        });
    }
}
