import React from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';
import { useRoute, useNavigation, RouteProp } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS } from '../constants';
import { MealLog } from '../types';

type ResultScreenRouteProp = RouteProp<{
    Result: { mealLog: MealLog };
}, 'Result'>;

export default function ResultScreen() {
    const route = useRoute<ResultScreenRouteProp>();
    const navigation = useNavigation<any>();
    const { mealLog } = route.params;
    const { nutrition, ai_advice } = mealLog;

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView contentContainerStyle={styles.scrollContent}>
                <View style={styles.header}>
                    <Text style={styles.title}>Results</Text>
                    <Text style={styles.subtitle}>Here's the breakdown of your meal</Text>
                </View>

                <View style={styles.card}>
                    <Text style={styles.dishName}>{mealLog.dish_name}</Text>

                    <View style={styles.divider} />

                    <View style={styles.macroContainer}>
                        <View style={styles.macroItem}>
                            <Text style={styles.macroValue}>{Math.round(nutrition.calories)}</Text>
                            <Text style={styles.macroLabel}>Calories</Text>
                        </View>
                        <View style={styles.macroItem}>
                            <Text style={styles.macroValue}>{Math.round(nutrition.protein)}g</Text>
                            <Text style={styles.macroLabel}>Protein</Text>
                        </View>
                        <View style={styles.macroItem}>
                            <Text style={styles.macroValue}>{Math.round(nutrition.carbs)}g</Text>
                            <Text style={styles.macroLabel}>Carbs</Text>
                        </View>
                        <View style={styles.macroItem}>
                            <Text style={styles.macroValue}>{Math.round(nutrition.fats)}g</Text>
                            <Text style={styles.macroLabel}>Fats</Text>
                        </View>
                    </View>
                </View>

                <View style={styles.adviceCard}>
                    <View style={styles.advisorHeader}>
                        <Text style={styles.advisorTitle}>🤖 AI Advisor Says:</Text>
                    </View>
                    <Text style={styles.adviceText}>{ai_advice}</Text>
                </View>

                <TouchableOpacity
                    style={styles.button}
                    onPress={() => navigation.navigate('Camera')}
                >
                    <Text style={styles.buttonText}>Scan Another Meal</Text>
                </TouchableOpacity>

            </ScrollView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.background,
    },
    scrollContent: {
        padding: 20,
    },
    header: {
        marginBottom: 20,
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        color: COLORS.primary,
    },
    subtitle: {
        fontSize: 16,
        color: COLORS.textSecondary,
    },
    card: {
        backgroundColor: COLORS.card,
        borderRadius: 20,
        padding: 20,
        marginBottom: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 5,
        elevation: 5,
    },
    dishName: {
        fontSize: 22,
        fontWeight: 'bold',
        textAlign: 'center',
        color: COLORS.text,
        marginBottom: 15,
    },
    divider: {
        height: 1,
        backgroundColor: '#E0E0E0',
        marginBottom: 15,
    },
    macroContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    macroItem: {
        alignItems: 'center',
    },
    macroValue: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.secondary,
    },
    macroLabel: {
        fontSize: 14,
        color: COLORS.textSecondary,
        marginTop: 4,
    },
    adviceCard: {
        backgroundColor: '#E8F5E9', // Light green
        borderRadius: 20,
        padding: 20,
        marginBottom: 30,
        borderWidth: 1,
        borderColor: '#C8E6C9',
    },
    advisorHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 10,
    },
    advisorTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.primary,
    },
    adviceText: {
        fontSize: 16,
        color: '#2E7D32',
        lineHeight: 24,
        fontStyle: 'italic',
    },
    button: {
        backgroundColor: COLORS.primary,
        padding: 18,
        borderRadius: 12,
        alignItems: 'center',
    },
    buttonText: {
        color: 'white',
        fontSize: 18,
        fontWeight: 'bold',
    },
});
